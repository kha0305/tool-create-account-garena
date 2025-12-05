const { pool } = require('../config/database');
const mailTmService = require('./mailTm');
const { generateUsername, generatePassword, generatePhone } = require('./accountGenerator');

let lastRateLimitTime = 0;
const RATE_LIMIT_COOLDOWN = 60000; // 60 seconds

// Simulate Garena creation
const createGarenaAccount = async (username, email, phone, password) => {
    // Simulate delay
    await new Promise(resolve => setTimeout(resolve, 1000 + Math.random() * 1000));
    // Simulate 95% success
    return {
        success: Math.random() > 0.05,
        username,
        email,
        phone,
        password
    };
};

const processAccountCreation = async (jobId, quantity, emailProvider = "mail.tm", usernamePrefix = null, usernameSeparator = ".") => {
    try {
        const [jobs] = await pool.query("SELECT * FROM creation_jobs WHERE job_id = ?", [jobId]);
        if (jobs.length === 0) return;

        // Check rate limit
        const timeSinceRateLimit = Date.now() - lastRateLimitTime;
        if (timeSinceRateLimit < RATE_LIMIT_COOLDOWN) {
            const waitTime = RATE_LIMIT_COOLDOWN - timeSinceRateLimit;
            console.log(`⏰ Recent rate limit, waiting ${waitTime/1000}s...`);
            await new Promise(resolve => setTimeout(resolve, waitTime));
        }

        for (let i = 0; i < quantity; i++) {
            const maxRetries = 3;
            let retryCount = 0;
            let success = false;
            
            while (retryCount < maxRetries && !success) {
                try {
                    const username = generateUsername(usernamePrefix, usernameSeparator, usernamePrefix ? i + 1 : null);
                    
                    // Email creation with retry
                    let emailData = null;
                    for (let attempt = 0; attempt < 3; attempt++) {
                        try {
                            // Only mail.tm for now
                            emailData = await mailTmService.createAccount();
                            break;
                        } catch (err) {
                            if (err.message.includes('429') || err.message.includes('Too Many')) {
                                lastRateLimitTime = Date.now();
                                const waitTime = 10000 * (attempt + 1);
                                console.warn(`⚠️ Rate limited by mail.tm, waiting ${waitTime/1000}s...`);
                                await new Promise(resolve => setTimeout(resolve, waitTime));
                            } else {
                                throw err;
                            }
                        }
                    }

                    if (!emailData) throw new Error("Failed to create email after 3 attempts");

                    const phone = generatePhone();
                    const password = generatePassword();
                    
                    const result = await createGarenaAccount(username, emailData.email, phone, password);

                    if (result.success) {
                        // Save account
                        const [res] = await pool.query(`
                            INSERT INTO garena_accounts 
                            (username, email, password, phone, status, email_provider, email_session_data, created_at)
                            VALUES (?, ?, ?, ?, ?, ?, ?, NOW())
                        `, [
                            username, 
                            emailData.email, 
                            password, 
                            phone, 
                            "created", 
                            emailProvider, 
                            JSON.stringify(emailData.session_data)
                        ]);
                        
                        const newId = res.insertId;
                        
                        // Update job
                        // Need to handle 'accounts' JSON array in MySQL
                        await pool.query(`
                           UPDATE creation_jobs 
                           SET completed = completed + 1,
                               accounts = JSON_ARRAY_APPEND(IFNULL(accounts, JSON_ARRAY()), '$', ?)
                           WHERE job_id = ?
                        `, [newId, jobId]);
                        
                        success = true;
                        console.log(`✅ Account ${i+1}/${quantity} created: ${emailData.email}`);
                    } else {
                        throw new Error("Garena creation failed (simulated)");
                    }

                } catch (e) {
                    retryCount++;
                    console.error(`Error creating account (attempt ${retryCount}): ${e.message}`);
                    if (retryCount >= maxRetries) {
                         await pool.query("UPDATE creation_jobs SET failed = failed + 1 WHERE job_id = ?", [jobId]);
                    } else {
                        await new Promise(resolve => setTimeout(resolve, 3000));
                    }
                }
            }

             // Delay between accounts
             if (i < quantity - 1) {
                let delay = 10000;
                if (quantity <= 2) delay = 5000;
                else if (quantity <= 5) delay = 8000;
                
                await new Promise(resolve => setTimeout(resolve, delay));
            }
        }

        await pool.query("UPDATE creation_jobs SET status = 'completed' WHERE job_id = ?", [jobId]);
        console.log(`✅ Job ${jobId} completed`);

    } catch (error) {
        console.error(`Job processing error: ${error.message}`);
        await pool.query("UPDATE creation_jobs SET status = 'failed' WHERE job_id = ?", [jobId]);
    }
};

module.exports = {
    processAccountCreation,
    getRateLimitStatus: () => {
        const timeSince = Date.now() - lastRateLimitTime;
        const cooldown = RATE_LIMIT_COOLDOWN;
        const inCooldown = timeSince < cooldown;
        return {
             status: inCooldown ? "rate_limited" : "ready",
             in_cooldown: inCooldown,
             remaining_seconds: inCooldown ? Math.ceil((cooldown - timeSince) / 1000) : 0
        };
    }
};
