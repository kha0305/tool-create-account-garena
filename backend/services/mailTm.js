const axios = require('axios');
const { v4: uuidv4 } = require('uuid'); // We might not need uuid if we generate random strings manually like python did

const BASE_URL = "https://api.mail.tm";

const generateRandomString = (length, chars) => {
    let result = '';
    for (let i = 0; i < length; i++) {
        result += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    return result;
};

const getDomains = async () => {
    try {
        const response = await axios.get(`${BASE_URL}/domains`);
        if (response.status === 200) {
            const domains = response.data['hydra:member'].map(d => d.domain);
            if (domains.length > 0) return domains;
        }
        return ["mail.tm"];
    } catch (error) {
        console.warn(`⚠️ get_domains error: ${error.message}`);
        return ["mail.tm"];
    }
};

const createAccount = async (username = null, password = null) => {
    try {
        const domains = await getDomains();
        const domain = domains[Math.floor(Math.random() * domains.length)];
        
        const chars = 'abcdefghijklmnopqrstuvwxyz0123456789';
        const uName = username || generateRandomString(10, chars);
        const pwd = password || generateRandomString(12, chars + 'ABCDEFGHIJKLMNOPQRSTUVWXYZ');
        const email = `${uName}@${domain}`;
        
        const payload = { address: email, password: pwd };
        
        // Create account
        const createRes = await axios.post(`${BASE_URL}/accounts`, payload);
        
        // Get token
        const tokenRes = await axios.post(`${BASE_URL}/token`, payload);
        const token = tokenRes.data.token;
        
        console.log(`✅ mail.tm account: ${email}`);
        
        return {
            email: email,
            password: pwd,
            session_data: {
                email: email,
                password: pwd,
                token: token,
                created_at: new Date().toISOString()
            }
        };
    } catch (error) {
        console.error(`❌ create_account error: ${error.message}`);
        if (error.response) {
            console.error(`Body: ${JSON.stringify(error.response.data)}`);
            throw new Error(`create_account failed ${error.response.status}`);
        }
        throw error;
    }
};

const getMessages = async (token) => {
    try {
        const response = await axios.get(`${BASE_URL}/messages`, {
            headers: { Authorization: `Bearer ${token}` }
        });
        
        const messages = response.data['hydra:member'] || [];
        // Filter out example.com
        return messages.filter(msg => {
            const sender = msg.from;
            let senderEmail = '';
            if (typeof sender === 'object') senderEmail = sender.address || '';
            else senderEmail = sender;
            return !senderEmail.endsWith('@example.com');
        });
    } catch (error) {
        console.error(`get_messages error: ${error.message}`);
        return [];
    }
};

const getMessageContent = async (messageId, token) => {
    try {
        const response = await axios.get(`${BASE_URL}/messages/${messageId}`, {
            headers: { Authorization: `Bearer ${token}` }
        });
        return response.data;
    } catch (error) {
        console.error(`get_message_content error: ${error.message}`);
        return null;
    }
};

module.exports = {
    getDomains,
    createAccount,
    getMessages,
    getMessageContent
};
