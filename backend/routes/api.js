const express = require('express');
const router = express.Router();
const { pool } = require('../config/database');
const mailTmService = require('../services/mailTm');
const { processAccountCreation, getRateLimitStatus } = require('../services/backgroundWorker');
const { generateUsername, generatePassword } = require('../services/accountGenerator');
const exceljs = require('exceljs');

// Helper to format date
const formatDate = (isoString) => {
    if (!isoString) return '';
    const date = new Date(isoString);
    return date.toLocaleString();
};

// Health
router.get('/health', (req, res) => {
    res.json({ ok: true, time: new Date().toISOString() });
});

// Debug MailTm
router.get('/debug/mailtm', async (req, res) => {
    const domains = await mailTmService.getDomains();
    res.json({ domains });
});

// Rate limit status
router.get('/rate-limit-status', (req, res) => {
    const status = getRateLimitStatus();
    if (status.in_cooldown) {
        res.json({
            ...status,
            message: `Vui lòng đợi ${status.remaining_seconds} giây trước khi tạo tài khoản mới`,
            recommendation: "Tạo 1-3 accounts mỗi lần để tránh rate limiting"
        });
    } else {
        res.json({
            ...status,
            message: "Sẵn sàng tạo tài khoản",
            recommendation: "Khuyên tạo 2-3 accounts mỗi lần"
        });
    }
});

// Create Accounts
router.post('/accounts/create', async (req, res) => {
    try {
        let { quantity, email_provider, username_prefix, username_separator } = req.body;
        quantity = parseInt(quantity);
        if (isNaN(quantity) || quantity < 1 || quantity > 100) {
            return res.status(400).json({ detail: "Quantity must be between 1 and 100" });
        }
        
        email_provider = email_provider || "mail.tm";
        username_separator = username_separator || ".";
        
        const [result] = await pool.query(`
            INSERT INTO creation_jobs (total, completed, failed, status, accounts, created_at)
            VALUES (?, 0, 0, 'processing', JSON_ARRAY(), NOW())
        `, [quantity]);
        
        const jobId = result.insertId;
        
        // Start background process
        processAccountCreation(jobId, quantity, email_provider, username_prefix, username_separator);
        
        res.json({
            job_id: jobId,
            message: `Started creating ${quantity} accounts with ${email_provider}`,
            status: "processing",
            email_provider
        });
        
    } catch (error) {
        console.error(error);
        res.status(500).json({ detail: "Failed to create job" });
    }
});

// Get Job Status
router.get('/accounts/job/:jobId', async (req, res) => {
    try {
        const [jobs] = await pool.query("SELECT * FROM creation_jobs WHERE job_id = ?", [req.params.jobId]);
        if (jobs.length === 0) return res.status(404).json({ detail: "Job not found" });
        
        const job = jobs[0];
        let accounts = [];
        
        // Parse accounts JSON if needed (MySQL returns it as array usually if column is JSON)
        // But if it's string (handled by driver?), ensure it's array
        let accountIds = job.accounts;
        if (typeof accountIds === 'string') accountIds = JSON.parse(accountIds);
        
        if (accountIds && accountIds.length > 0) {
            // Fetch accounts details
            // Clean logic: use IN clause
            const [accRows] = await pool.query(`SELECT * FROM garena_accounts WHERE id IN (?)`, [accountIds]);
            accounts = accRows;
        }
        
        const progress = job.total > 0 ? (job.completed / job.total) * 100 : 0;
        
        res.json({
            job_id: job.job_id,
            total: job.total,
            completed: job.completed,
            failed: job.failed,
            status: job.status,
            progress_percentage: progress,
            accounts: accounts
        });
        
    } catch (error) {
        console.error(error);
        res.status(500).json({ detail: error.message });
    }
});

// Get All Accounts
router.get('/accounts', async (req, res) => {
    try {
        const [accounts] = await pool.query("SELECT * FROM garena_accounts ORDER BY id ASC LIMIT 1000");
        res.json(accounts);
    } catch (error) {
        console.error(error);
        res.status(500).json({ detail: error.message });
    }
});

// Delete account
router.delete('/accounts/:id', async (req, res) => {
    try {
        const [result] = await pool.query("DELETE FROM garena_accounts WHERE id = ?", [req.params.id]);
        if (result.affectedRows === 0) return res.status(404).json({ detail: "Account not found" });
        res.json({ message: "Account deleted successfully" });
    } catch (error) {
        res.status(500).json({ detail: error.message });
    }
});

// Delete all
router.delete('/accounts', async (req, res) => {
    try {
        const [result] = await pool.query("DELETE FROM garena_accounts");
        res.json({ message: `Deleted ${result.affectedRows} accounts` });
    } catch (error) {
        res.status(500).json({ detail: error.message });
    }
});

// Delete multiple
router.post('/accounts/delete-multiple', async (req, res) => {
    try {
        const accountIds = req.body; // Expecting array of ints
        if (!Array.isArray(accountIds) || accountIds.length === 0) {
            return res.status(400).json({ detail: "No account IDs provided" });
        }
        
        const [result] = await pool.query("DELETE FROM garena_accounts WHERE id IN (?)", [accountIds]);
        if (result.affectedRows === 0) return res.status(404).json({ detail: "No accounts found or deleted" });
        
        res.json({ message: `Deleted ${result.affectedRows} accounts successfully`, deleted_count: result.affectedRows });
    } catch (error) {
        res.status(500).json({ detail: error.message });
    }
});

// Verify login (mark status)
router.post('/accounts/:id/verify-login', async (req, res) => {
    try {
        const [accounts] = await pool.query("SELECT * FROM garena_accounts WHERE id = ?", [req.params.id]);
        if (accounts.length === 0) return res.status(404).json({ detail: "Account not found" });
        
        await pool.query("UPDATE garena_accounts SET status = 'pending_verification' WHERE id = ?", [req.params.id]);
        
        const account = accounts[0];
        res.json({
            message: "Account ready for verification",
            login_url: "https://sso.garena.com/universal/login?app_id=10100&redirect_uri=https://account.garena.com/?locale_name=SG&locale=vi-VN",
            account: {
                username: account.username,
                email: account.email,
                phone: account.phone,
                password: account.password
            }
        });
    } catch (error) {
        res.status(500).json({ detail: error.message });
    }
});

// Regenerate Email
router.put('/accounts/:id/regenerate', async (req, res) => {
    try {
        const id = req.params.id;
        const [accounts] = await pool.query("SELECT * FROM garena_accounts WHERE id = ?", [id]);
        if (accounts.length === 0) return res.status(404).json({ detail: "Account not found" });
        const account = accounts[0];

        // Rate limit check
        const { in_cooldown, remaining_seconds } = getRateLimitStatus();
        if (in_cooldown) {
            return res.status(429).json({ detail: `Rate limited. Please wait ${remaining_seconds} seconds.` });
        }
        
        // Generate new
        const newUsername = generateUsername();
        const newPassword = generatePassword();
        
        let result = null;
        try {
            // Need retry logic here? simpler for now
             result = await mailTmService.createAccount(newUsername, newPassword);
        } catch (e) {
             return res.status(429).json({ detail: "Mail.tm API rate limit reached or error." });
        }
        
        await pool.query(`
            UPDATE garena_accounts 
            SET username = ?, email = ?, password = ?, email_provider = 'mail.tm', email_session_data = ?, updated_at = NOW()
            WHERE id = ?
        `, [newUsername, result.email, newPassword, JSON.stringify(result.session_data), id]);
        
        res.json({
            message: "Email regenerated successfully",
            account_id: id,
            old_email: account.email,
            new_email: result.email,
            new_username: newUsername
        });
        
    } catch (error) {
        res.status(500).json({ detail: error.message });
    }
});

// Check inbox
router.get('/accounts/:id/inbox', async (req, res) => {
    try {
        const [accounts] = await pool.query("SELECT * FROM garena_accounts WHERE id = ?", [req.params.id]);
        if (accounts.length === 0) return res.status(404).json({ detail: "Account not found" });
        const account = accounts[0];
        
        const sessionData = typeof account.email_session_data === 'string' 
            ? JSON.parse(account.email_session_data) 
            : account.email_session_data;
            
        if (!sessionData || !sessionData.token) {
            return res.json({
                account_id: account.id,
                email: account.email,
                messages: [],
                error: "No session data available"
            });
        }
        
        const messages = await mailTmService.getMessages(sessionData.token);
        res.json({
            account_id: account.id,
            email: account.email,
            provider: account.email_provider,
            messages: messages,
            count: messages.length
        });
        
    } catch (error) {
        res.status(500).json({ detail: error.message });
    }
});

// Get message content
router.get('/accounts/:id/inbox/:msgId', async (req, res) => {
    try {
        const [accounts] = await pool.query("SELECT * FROM garena_accounts WHERE id = ?", [req.params.id]);
        if (accounts.length === 0) return res.status(404).json({ detail: "Account not found" });
        const account = accounts[0];
        
        const sessionData = typeof account.email_session_data === 'string' 
            ? JSON.parse(account.email_session_data) 
            : account.email_session_data;
            
        if (!sessionData || !sessionData.token) {
            return res.status(400).json({ detail: "No session data" });
        }
        
        const content = await mailTmService.getMessageContent(req.params.msgId, sessionData.token);
        if (!content) return res.status(404).json({ detail: "Message not found" });
        
        res.json({
            account_id: account.id,
            message: content
        });
    } catch (error) {
        res.status(500).json({ detail: error.message });
    }
});

// Export TXT
router.get('/accounts/export/txt', async (req, res) => {
    try {
        const [accounts] = await pool.query("SELECT * FROM garena_accounts ORDER BY id ASC LIMIT 1000");
        if (accounts.length === 0) return res.status(404).json({ detail: "No accounts" });
        
        const lines = accounts.map(acc => {
            const timeStr = new Date(acc.created_at).toLocaleString('en-GB', { day: '2-digit', month: '2-digit', year: '2-digit', hour: '2-digit', minute: '2-digit' }).replace(',', ''); // dd-mm-yy hh:mm roughly
            // Python used strftime("%d-%m-%y %H:%M")
             const d = new Date(acc.created_at);
             const formattedTime = `${String(d.getDate()).padStart(2,'0')}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getFullYear()).slice(-2)} ${String(d.getHours()).padStart(2,'0')}:${String(d.getMinutes()).padStart(2,'0')}`;
            return `${acc.username}|${acc.password}|${acc.email}|Tạo lúc: ${formattedTime}`;
        });
        
        const content = lines.join('\n');
        const filename = `ACCOUNTS_${accounts.length}.txt`;
        
        res.setHeader('Content-Type', 'text/plain');
        res.setHeader('Content-Disposition', `attachment; filename=${filename}`);
        res.send(content);
        
    } catch (error) {
        res.status(500).json({ detail: error.message });
    }
});

// Export CSV
router.get('/accounts/export/csv', async (req, res) => {
    try {
         const [accounts] = await pool.query("SELECT * FROM garena_accounts ORDER BY id ASC LIMIT 1000");
         if (accounts.length === 0) return res.status(404).json({ detail: "No accounts" });
         
         const header = "Username,Email,Password,Phone,Status,Provider,Created At";
         const lines = accounts.map(acc => {
             const createdStr = new Date(acc.created_at).toISOString().replace('T', ' ').substring(0, 19);
             return `${acc.username},${acc.email},${acc.password},${acc.phone || ''},${acc.status || ''},${acc.email_provider || ''},${createdStr}`;
         });
         
         const content = [header, ...lines].join('\n');
         const filename = `ACCOUNTS_${accounts.length}.csv`;
         
         res.setHeader('Content-Type', 'text/csv');
         res.setHeader('Content-Disposition', `attachment; filename=${filename}`);
         res.send(content);
         
    } catch (error) {
        res.status(500).json({ detail: error.message });
    }
});

// Export XLSX
router.get('/accounts/export/xlsx', async (req, res) => {
    try {
        const [accounts] = await pool.query("SELECT * FROM garena_accounts ORDER BY id ASC LIMIT 1000");
        if (accounts.length === 0) return res.status(404).json({ detail: "No accounts" });
        
        const workbook = new exceljs.Workbook();
        const sheet = workbook.addWorksheet('Accounts');
        
        sheet.columns = [
            { header: 'ID', key: 'id', width: 10 },
            { header: 'Username', key: 'username', width: 20 },
            { header: 'Password', key: 'password', width: 20 },
            { header: 'Email', key: 'email', width: 30 },
            { header: 'Phone', key: 'phone', width: 15 },
            { header: 'Status', key: 'status', width: 15 },
            { header: 'Created At', key: 'created_at', width: 20 }
        ];
        
        accounts.forEach(acc => {
            sheet.addRow({
                id: acc.id,
                username: acc.username,
                password: acc.password,
                email: acc.email,
                phone: acc.phone,
                status: acc.status,
                created_at: acc.created_at
            });
        });
        
        const filename = `ACCOUNTS_${accounts.length}.xlsx`;
        
        res.setHeader('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet');
        res.setHeader('Content-Disposition', `attachment; filename=${filename}`);
        
        await workbook.xlsx.write(res);
        res.end();
        
    } catch (error) {
        res.status(500).json({ detail: error.message });
    }
});

module.exports = router;
