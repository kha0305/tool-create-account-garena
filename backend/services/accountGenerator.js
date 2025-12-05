const crypto = require('crypto');

const generateUsername = (customPrefix = null, separator = '.', counter = null) => {
    if (customPrefix && counter !== null) {
        return `${customPrefix}${separator}${counter}`;
    } else {
        const prefixes = ['gamer', 'player', 'user', 'pro', 'master'];
        const prefix = prefixes[Math.floor(Math.random() * prefixes.length)];
        const suffix = Math.floor(100000 + Math.random() * 900000).toString(); // 6 random digits
        return `${prefix}${suffix}`;
    }
};

const generatePassword = () => {
    const lowercase = 'abcdefghijklmnopqrstuvwxyz';
    const uppercase = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
    const digits = '0123456789';
    const symbols = '!@#$%^&*';
    
    let chars = [
        lowercase[Math.floor(Math.random() * lowercase.length)],
        uppercase[Math.floor(Math.random() * uppercase.length)],
        digits[Math.floor(Math.random() * digits.length)],
        symbols[Math.floor(Math.random() * symbols.length)]
    ];
    
    const allChars = lowercase + uppercase + digits + symbols;
    for (let i = 0; i < 8; i++) {
        chars.push(allChars[Math.floor(Math.random() * allChars.length)]);
    }
    
    // Shuffle
    chars = chars.sort(() => 0.5 - Math.random());
    
    return chars.join('');
};

const generatePhone = () => {
    const prefixes = ['03', '05', '07', '08', '09'];
    const prefix = prefixes[Math.floor(Math.random() * prefixes.length)];
    
    const middle = Math.floor(1000 + Math.random() * 9000).toString();
    const end = Math.floor(1000 + Math.random() * 9000).toString();
    
    return `+84-${prefix}${middle.substring(0, 1)}-${middle.substring(1)}-${end}`;
};

module.exports = {
    generateUsername,
    generatePassword,
    generatePhone
};
