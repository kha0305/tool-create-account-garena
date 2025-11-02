import { useState, useEffect } from 'react';
import axios from 'axios';
import { toast } from 'sonner';
import { Loader2, Trash2, Download, Zap, Database, Sun, Moon, ExternalLink, CheckCircle2, Mail, Inbox, Copy, Check } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Progress } from '@/components/ui/progress';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog';

const API_BASE_URL = process.env.REACT_APP_BACKEND_URL || "http://localhost:8001";
const API = `${API_BASE_URL}/api`;

const Dashboard = () => {
  const [quantity, setQuantity] = useState('5');
  const [emailProvider, setEmailProvider] = useState('mail.tm');
  const [creating, setCreating] = useState(false);
  const [currentJob, setCurrentJob] = useState(null);
  const [accounts, setAccounts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [stats, setStats] = useState({ total: 0, created: 0 });
  const [theme, setTheme] = useState(() => {
    return localStorage.getItem('theme') || 'dark';
  });
  const [verifyDialog, setVerifyDialog] = useState(false);
  const [selectedAccount, setSelectedAccount] = useState(null);
  const [inboxDialog, setInboxDialog] = useState(false);
  const [inboxMessages, setInboxMessages] = useState([]);
  const [checkingInbox, setCheckingInbox] = useState(false);
  const [copiedItems, setCopiedItems] = useState({}); // Track copied items
  const [emailContentDialog, setEmailContentDialog] = useState(false);
  const [selectedEmail, setSelectedEmail] = useState(null);
  const [loadingEmailContent, setLoadingEmailContent] = useState(false);
  const [emailViewMode, setEmailViewMode] = useState('text'); // 'text' or 'html'
  const [exportFormat, setExportFormat] = useState('txt'); // 'txt', 'csv', or 'xlsx'
  
  // Custom username states
  const [usernamePrefix, setUsernamePrefix] = useState('');
  const [usernameSeparator, setUsernameSeparator] = useState('.');
  
  // Bulk delete states
  const [selectedAccounts, setSelectedAccounts] = useState([]);
  const [isDeleting, setIsDeleting] = useState(false);

  // Quantity options
  const quantities = [1, 5, 10, 15, 20, 25, 30, 40, 50, 60, 70, 80, 90, 100];

  // Email providers - only mail.tm now
  const emailProviders = [
    { id: 'mail.tm', name: 'Mail.tm', icon: '📧' }
  ];

  // Apply theme
  useEffect(() => {
    document.body.className = theme;
    localStorage.setItem('theme', theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme(prev => prev === 'dark' ? 'light' : 'dark');
  };

  // Fetch accounts
  const fetchAccounts = async () => {
    try {
      const response = await axios.get(`${API}/accounts`);
      setAccounts(response.data);
      setStats({
        total: response.data.length,
        created: response.data.filter(a => a.status === 'created').length
      });
    } catch (error) {
      console.error('Error fetching accounts:', error);
    }
  };

  // Poll job status
  const pollJobStatus = async (jobId) => {
    const interval = setInterval(async () => {
      try {
        const response = await axios.get(`${API}/accounts/job/${jobId}`);
        const jobData = response.data;
        
        setCurrentJob(jobData);
        
        if (jobData.status === 'completed') {
          clearInterval(interval);
          setCreating(false);
          setCurrentJob(null);
          await fetchAccounts();
          toast.success(`Đã tạo thành công ${jobData.completed} tài khoản!`);
        }
      } catch (error) {
        console.error('Error polling job:', error);
        clearInterval(interval);
        setCreating(false);
      }
    }, 1500);

    return interval;
  };

  // Create accounts
  const handleCreateAccounts = async () => {
    if (!quantity) {
      toast.error('Vui lòng chọn số lượng tài khoản');
      return;
    }

    const qty = parseInt(quantity);
    
    // Warning for any batch - emphasize rate limiting
    if (qty > 5) {
      toast.warning('⚠️ Tạo nhiều tài khoản sẽ mất thời gian do giới hạn API của Mail.tm. Mỗi tài khoản cần ~10-15 giây. Vui lòng kiên nhẫn!', {
        duration: 6000
      });
    } else if (qty > 1) {
      toast.info('ℹ️ Đang tạo từng tài khoản một để tránh rate limiting. Vui lòng đợi!', {
        duration: 4000
      });
    }

    setCreating(true);
    try {
      const requestData = {
        quantity: qty,
        email_provider: emailProvider
      };
      
      // Add username customization if prefix is provided
      if (usernamePrefix && usernamePrefix.trim()) {
        requestData.username_prefix = usernamePrefix.trim();
        requestData.username_separator = usernameSeparator;
      }
      
      const response = await axios.post(`${API}/accounts/create`, requestData);

      const estimatedTime = qty * 10; // Updated estimate: 10 seconds per account
      const minutes = Math.ceil(estimatedTime / 60);
      toast.success(`✅ Đã bắt đầu tạo ${qty} tài khoản (dự kiến ~${minutes} phút)`, {
        duration: 4000
      });
      pollJobStatus(response.data.job_id);
    } catch (error) {
      const errorMsg = error.response?.data?.detail || error.message || 'Lỗi không xác định';
      
      if (errorMsg.includes('429') || errorMsg.includes('rate limit')) {
        toast.error('⚠️ API Mail.tm đang bị giới hạn. Vui lòng đợi 1-2 phút rồi thử lại!', {
          duration: 6000
        });
      } else {
        toast.error('❌ Lỗi khi tạo tài khoản. Vui lòng thử lại sau!');
      }
      
      setCreating(false);
      console.error(error);
    }
  };

  // Delete account
  const handleDeleteAccount = async (accountId) => {
    try {
      await axios.delete(`${API}/accounts/${accountId}`);
      toast.success('Đã xóa tài khoản');
      await fetchAccounts();
    } catch (error) {
      toast.error('Lỗi khi xóa tài khoản');
      console.error(error);
    }
  };

  // Delete all accounts
  const handleDeleteAll = async () => {
    if (!window.confirm('Bạn có chắc muốn xóa tất cả tài khoản?')) return;
    
    try {
      await axios.delete(`${API}/accounts`);
      toast.success('Đã xóa tất cả tài khoản');
      await fetchAccounts();
    } catch (error) {
      toast.error('Lỗi khi xóa tài khoản');
      console.error(error);
    }
  };

  // Handle verify login
  const handleVerifyLogin = (account) => {
    setSelectedAccount(account);
    setVerifyDialog(true);
  };

  // Open Garena login page
  const openGarenaLogin = () => {
    if (!selectedAccount) return;

    const loginUrl = `https://sso.garena.com/universal/login?app_id=10100&redirect_uri=https://account.garena.com/?locale_name=SG&locale=vi-VN`;
    
    // Open in new tab
    window.open(loginUrl, '_blank');
    
    // Copy credentials to clipboard
    const credentials = `Username: ${selectedAccount.username}\nEmail: ${selectedAccount.email}\nPassword: ${selectedAccount.password}`;
    navigator.clipboard.writeText(credentials);
    
    toast.success('Đã mở trang đăng nhập và copy thông tin!');
    
    // Update status to pending verification
    axios.post(`${API}/accounts/${selectedAccount.id}/verify`)
      .then(() => {
        fetchAccounts();
      })
      .catch(err => console.error(err));
  };

  // Check inbox for account
  const handleCheckInbox = async (account) => {
    setSelectedAccount(account);
    setCheckingInbox(true);
    setInboxDialog(true);
    setInboxMessages([]);

    try {
      const response = await axios.get(`${API}/accounts/${account.id}/inbox`);
      setInboxMessages(response.data.messages || []);
      
      if (response.data.error || response.data.info) {
        toast.info(response.data.error || response.data.info);
      } else if (response.data.messages.length === 0) {
        toast.info('Inbox trống - chưa có email nào');
      } else {
        toast.success(`Tìm thấy ${response.data.messages.length} email`);
      }
    } catch (error) {
      console.error('Error checking inbox:', error);
      toast.error('Lỗi khi kiểm tra inbox');
    } finally {
      setCheckingInbox(false);
    }
  };

  // View email content
  const handleViewEmailContent = async (message) => {
    setSelectedEmail(null);
    setLoadingEmailContent(true);
    setEmailContentDialog(true);
    setEmailViewMode('html'); // Default to HTML view

    try {
      const response = await axios.get(`${API}/accounts/${selectedAccount.id}/inbox/${message.id}`);
      setSelectedEmail(response.data.message);
      toast.success('Đã tải nội dung email');
    } catch (error) {
      console.error('Error loading email content:', error);
      toast.error('Lỗi khi tải nội dung email');
    } finally {
      setLoadingEmailContent(false);
    }
  };

  // Export accounts
  const handleExport = async (format) => {
    if (accounts.length === 0) {
      toast.error('Không có tài khoản để xuất');
      return;
    }

    try {
      const response = await axios.get(`${API}/accounts/export/${format}`, {
        responseType: 'blob'
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      
      // Extract filename from Content-Disposition header or use default
      const contentDisposition = response.headers['content-disposition'];
      let filename = `ACCOUNTS_${accounts.length}.${format}`;
      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename=([^;]+)/);
        if (filenameMatch && filenameMatch[1]) {
          filename = filenameMatch[1].replace(/['"]/g, '');
        }
      }
      
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      
      toast.success(`Đã xuất file ${format.toUpperCase()}`);
    } catch (error) {
      console.error('Error exporting:', error);
      toast.error(`Lỗi khi xuất file ${format.toUpperCase()}`);
    }
  };

  // Copy to clipboard function
  const handleCopyToClipboard = (text, itemKey) => {
    navigator.clipboard.writeText(text).then(() => {
      setCopiedItems(prev => ({ ...prev, [itemKey]: true }));
      toast.success('Đã sao chép!');
      
      // Reset copied state after 2 seconds
      setTimeout(() => {
        setCopiedItems(prev => ({ ...prev, [itemKey]: false }));
      }, 2000);
    }).catch(err => {
      console.error('Failed to copy:', err);
      toast.error('Lỗi khi sao chép');
    });
  };

  // Load accounts on mount
  useEffect(() => {
    fetchAccounts();
  }, []);

  return (
    <div className={`min-h-screen p-4 md:p-8 relative App ${theme}`}>
      {/* Theme Toggle */}
      <button 
        onClick={toggleTheme} 
        className={`theme-toggle ${theme}`}
        data-testid="theme-toggle-button"
        title={theme === 'dark' ? 'Chuyển sang sáng' : 'Chuyển sang tối'}
      >
        {theme === 'dark' ? <Sun size={20} /> : <Moon size={20} />}
      </button>

      {/* Header */}
      <div className="max-w-7xl mx-auto mb-8 fade-in relative z-10">
        <div className="text-center mb-8">
          <h1 className={`text-4xl md:text-5xl lg:text-6xl font-bold mb-4 glow-text ${theme}`} data-testid="page-title">
            Garena Account Creator
          </h1>
          <p className={`text-base md:text-lg ${theme === 'dark' ? 'text-gray-300' : 'text-gray-600'}`} data-testid="page-subtitle">
            Công cụ tạo tài khoản Garena hàng loạt với email ảo
          </p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          <Card className={`glass-card ${theme} border-0`}>
            <CardHeader className="pb-3">
              <CardTitle className={`text-sm font-medium ${theme === 'dark' ? 'text-gray-400' : 'text-gray-600'}`}>Tổng tài khoản</CardTitle>
            </CardHeader>
            <CardContent>
              <div className={`text-3xl font-bold ${theme === 'dark' ? 'text-cyan-400' : 'text-cyan-600'}`} data-testid="total-accounts">{stats.total}</div>
            </CardContent>
          </Card>

          <Card className={`glass-card ${theme} border-0`}>
            <CardHeader className="pb-3">
              <CardTitle className={`text-sm font-medium ${theme === 'dark' ? 'text-gray-400' : 'text-gray-600'}`}>Đã tạo thành công</CardTitle>
            </CardHeader>
            <CardContent>
              <div className={`text-3xl font-bold ${theme === 'dark' ? 'text-green-400' : 'text-green-600'}`} data-testid="created-accounts">{stats.created}</div>
            </CardContent>
          </Card>

          <Card className={`glass-card ${theme} border-0`}>
            <CardHeader className="pb-3">
              <CardTitle className={`text-sm font-medium ${theme === 'dark' ? 'text-gray-400' : 'text-gray-600'}`}>Trạng thái</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold" data-testid="system-status">
                {creating ? (
                  <span className={`${theme === 'dark' ? 'text-blue-400' : 'text-blue-600'} flex items-center gap-2`}>
                    <Loader2 className="animate-spin" size={24} />
                    Đang xử lý
                  </span>
                ) : (
                  <span className={theme === 'dark' ? 'text-green-400' : 'text-green-600'}>Sẵn sàng</span>
                )}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Creation Panel */}
        <Card className={`glass-card ${theme} border-0 mb-8`}>
          <CardHeader>
            <CardTitle className={`flex items-center gap-2 ${theme === 'dark' ? 'text-gray-100' : 'text-gray-900'}`}>
              <Zap className={theme === 'dark' ? 'text-cyan-400' : 'text-cyan-600'} size={24} />
              Tạo tài khoản mới
            </CardTitle>
            <CardDescription className={theme === 'dark' ? 'text-gray-400' : 'text-gray-600'}>Chọn số lượng và bắt đầu tạo tài khoản</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex flex-col gap-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="flex-1">
                  <label className={`block text-sm font-medium mb-2 ${theme === 'dark' ? 'text-gray-300' : 'text-gray-700'}`}>Số lượng tài khoản</label>
                  <Select value={quantity} onValueChange={setQuantity} disabled={creating}>
                    <SelectTrigger className={`w-full ${theme === 'dark' ? 'bg-gray-800/50 border-gray-700 text-gray-100' : 'bg-white border-gray-300 text-gray-900'}`} data-testid="quantity-select">
                      <SelectValue placeholder="Chọn số lượng" />
                    </SelectTrigger>
                    <SelectContent className={theme === 'dark' ? 'bg-gray-900 border-gray-700' : 'bg-white border-gray-200'}>
                      {quantities.map(q => (
                        <SelectItem key={q} value={q.toString()} data-testid={`quantity-option-${q}`} className={theme === 'dark' ? 'text-gray-100' : 'text-gray-900'}>
                          {q} tài khoản
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div className="flex-1">
                  <label className={`block text-sm font-medium mb-2 ${theme === 'dark' ? 'text-gray-300' : 'text-gray-700'}`}>Dịch vụ Email</label>
                  <Select value={emailProvider} onValueChange={setEmailProvider} disabled={creating}>
                    <SelectTrigger className={`w-full ${theme === 'dark' ? 'bg-gray-800/50 border-gray-700 text-gray-100' : 'bg-white border-gray-300 text-gray-900'}`} data-testid="email-provider-select">
                      <SelectValue placeholder="Chọn dịch vụ email" />
                    </SelectTrigger>
                    <SelectContent className={theme === 'dark' ? 'bg-gray-900 border-gray-700' : 'bg-white border-gray-200'}>
                      {emailProviders.map(provider => (
                        <SelectItem key={provider.id} value={provider.id} data-testid={`provider-option-${provider.id}`} className={theme === 'dark' ? 'text-gray-100' : 'text-gray-900'}>
                          {provider.icon} {provider.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>
              <Button
                onClick={handleCreateAccounts}
                disabled={creating}
                className={`cyber-button ${theme} h-10 w-full md:w-auto`}
                data-testid="create-accounts-button"
              >
                {creating ? (
                  <>
                    <Loader2 className="mr-2 animate-spin" size={18} />
                    Đang tạo...
                  </>
                ) : (
                  <>
                    <Zap className="mr-2" size={18} />
                    Bắt đầu tạo
                  </>
                )}
              </Button>
            </div>

            {/* Progress Bar */}
            {currentJob && (
              <div className="mt-6 fade-in" data-testid="progress-section">
                <div className="flex justify-between text-sm mb-2">
                  <span className={theme === 'dark' ? 'text-gray-400' : 'text-gray-600'}>Tiến độ: {currentJob.completed}/{currentJob.total}</span>
                  <span className={`font-semibold ${theme === 'dark' ? 'text-cyan-400' : 'text-cyan-600'}`}>{currentJob.progress_percentage.toFixed(1)}%</span>
                </div>
                <Progress value={currentJob.progress_percentage} className="h-2" data-testid="progress-bar" />
                {currentJob.failed > 0 && (
                  <p className={`text-sm mt-2 ${theme === 'dark' ? 'text-red-400' : 'text-red-600'}`} data-testid="failed-count">Thất bại: {currentJob.failed}</p>
                )}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Accounts Table */}
        <Card className={`glass-card ${theme} border-0`}>
          <CardHeader>
            <div className="flex justify-between items-center">
              <div className="flex items-center gap-2">
                <Database className={theme === 'dark' ? 'text-cyan-400' : 'text-cyan-600'} size={24} />
                <CardTitle className={theme === 'dark' ? 'text-gray-100' : 'text-gray-900'}>Danh sách tài khoản</CardTitle>
              </div>
              <div className="flex gap-2">
                <Select value={exportFormat} onValueChange={setExportFormat}>
                  <SelectTrigger className={`w-32 ${theme === 'dark' ? 'bg-gray-800/50 border-gray-700 text-gray-100' : 'bg-white border-gray-300 text-gray-900'}`}>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent className={theme === 'dark' ? 'bg-gray-900 border-gray-700' : 'bg-white border-gray-200'}>
                    <SelectItem value="txt" className={theme === 'dark' ? 'text-gray-100' : 'text-gray-900'}>TXT</SelectItem>
                    <SelectItem value="csv" className={theme === 'dark' ? 'text-gray-100' : 'text-gray-900'}>CSV</SelectItem>
                    <SelectItem value="xlsx" className={theme === 'dark' ? 'text-gray-100' : 'text-gray-900'}>XLSX</SelectItem>
                  </SelectContent>
                </Select>
                <Button
                  onClick={() => handleExport(exportFormat)}
                  variant="outline"
                  size="sm"
                  className={theme === 'dark' ? 'bg-green-900/20 hover:bg-green-900/40 border-green-700 text-green-400' : 'bg-green-50 hover:bg-green-100 border-green-300 text-green-700'}
                  disabled={accounts.length === 0}
                  data-testid="export-button"
                >
                  <Download className="mr-2" size={16} />
                  Xuất File
                </Button>
                <Button
                  onClick={handleDeleteAll}
                  variant="outline"
                  size="sm"
                  className={theme === 'dark' ? 'bg-red-900/20 hover:bg-red-900/40 border-red-700 text-red-400' : 'bg-red-50 hover:bg-red-100 border-red-300 text-red-700'}
                  disabled={accounts.length === 0}
                  data-testid="delete-all-button"
                >
                  <Trash2 className="mr-2" size={16} />
                  Xóa tất cả
                </Button>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              {accounts.length === 0 ? (
                <div className={`text-center py-12 ${theme === 'dark' ? 'text-gray-500' : 'text-gray-400'}`} data-testid="no-accounts-message">
                  <Database size={48} className="mx-auto mb-4 opacity-50" />
                  <p>Chưa có tài khoản nào. Hãy tạo tài khoản mới!</p>
                </div>
              ) : (
                <table className={`cyber-table ${theme}`} data-testid="accounts-table">
                  <thead>
                    <tr>
                      <th>Username</th>
                      <th>Email</th>
                      <th>Mật khẩu</th>
                      <th>Provider</th>
                      <th>Trạng thái</th>
                      <th>Ngày tạo</th>
                      <th>Thao tác</th>
                    </tr>
                  </thead>
                  <tbody>
                    {accounts.map((account, index) => (
                      <tr key={account.id} data-testid={`account-row-${index}`}>
                        <td className={`font-semibold ${theme === 'dark' ? 'text-cyan-400' : 'text-cyan-700'}`} data-testid={`account-username-${index}`}>
                          <div className="flex items-center gap-2">
                            <span>{account.username}</span>
                            <button
                              onClick={() => handleCopyToClipboard(account.username, `username-${account.id}`)}
                              className={`p-1 rounded hover:bg-gray-700/50 transition-colors ${theme === 'dark' ? 'text-gray-400 hover:text-cyan-400' : 'text-gray-500 hover:text-cyan-600'}`}
                              title="Sao chép username"
                            >
                              {copiedItems[`username-${account.id}`] ? <Check size={14} className="text-green-500" /> : <Copy size={14} />}
                            </button>
                          </div>
                        </td>
                        <td className="text-sm" data-testid={`account-email-${index}`}>
                          <div className="flex items-center gap-2">
                            <span className="truncate max-w-[200px]">{account.email}</span>
                            <button
                              onClick={() => handleCopyToClipboard(account.email, `email-${account.id}`)}
                              className={`p-1 rounded hover:bg-gray-700/50 transition-colors ${theme === 'dark' ? 'text-gray-400 hover:text-cyan-400' : 'text-gray-500 hover:text-cyan-600'}`}
                              title="Sao chép email"
                            >
                              {copiedItems[`email-${account.id}`] ? <Check size={14} className="text-green-500" /> : <Copy size={14} />}
                            </button>
                          </div>
                        </td>
                        <td className="text-sm font-mono" data-testid={`account-password-${index}`}>
                          <div className="flex items-center gap-2">
                            <span>{account.password}</span>
                            <button
                              onClick={() => handleCopyToClipboard(account.password, `password-${account.id}`)}
                              className={`p-1 rounded hover:bg-gray-700/50 transition-colors ${theme === 'dark' ? 'text-gray-400 hover:text-cyan-400' : 'text-gray-500 hover:text-cyan-600'}`}
                              title="Sao chép password"
                            >
                              {copiedItems[`password-${account.id}`] ? <Check size={14} className="text-green-500" /> : <Copy size={14} />}
                            </button>
                          </div>
                        </td>
                        <td className="text-xs">
                          <span className={`px-2 py-1 rounded text-xs ${theme === 'dark' ? 'bg-purple-900/30 text-purple-300' : 'bg-purple-100 text-purple-700'}`}>
                            📧 Mail.tm
                          </span>
                        </td>
                        <td>
                          <span className={`status-badge status-${account.status} ${theme}`} data-testid={`account-status-${index}`}>
                            {account.status === 'pending_verification' ? 'Chờ xác thực' : account.status}
                          </span>
                        </td>
                        <td className="text-sm" data-testid={`account-created-${index}`}>
                          {new Date(account.created_at).toLocaleString('vi-VN')}
                        </td>
                        <td>
                          <div className="flex gap-1">
                            <Button
                              onClick={() => handleCheckInbox(account)}
                              variant="ghost"
                              size="sm"
                              className={theme === 'dark' ? 'text-blue-400 hover:text-blue-300 hover:bg-blue-900/20' : 'text-blue-600 hover:text-blue-700 hover:bg-blue-50'}
                              data-testid={`check-inbox-button-${index}`}
                              title="Kiểm tra inbox"
                            >
                              <Inbox size={16} />
                            </Button>
                            <Button
                              onClick={() => handleVerifyLogin(account)}
                              variant="ghost"
                              size="sm"
                              className={theme === 'dark' ? 'text-green-400 hover:text-green-300 hover:bg-green-900/20' : 'text-green-600 hover:text-green-700 hover:bg-green-50'}
                              data-testid={`verify-account-button-${index}`}
                              title="Kiểm tra đăng nhập"
                            >
                              <ExternalLink size={16} />
                            </Button>
                            <Button
                              onClick={() => handleDeleteAccount(account.id)}
                              variant="ghost"
                              size="sm"
                              className={theme === 'dark' ? 'text-red-400 hover:text-red-300 hover:bg-red-900/20' : 'text-red-600 hover:text-red-700 hover:bg-red-50'}
                              data-testid={`delete-account-button-${index}`}
                              title="Xóa tài khoản"
                            >
                              <Trash2 size={16} />
                            </Button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Verify Dialog */}
      <Dialog open={verifyDialog} onOpenChange={setVerifyDialog}>
        <DialogContent className={theme === 'dark' ? 'bg-gray-900 border-gray-700' : 'bg-white border-gray-200'}>
          <DialogHeader>
            <DialogTitle className={theme === 'dark' ? 'text-gray-100' : 'text-gray-900'}>
              Kiểm tra đăng nhập Garena
            </DialogTitle>
            <DialogDescription className={theme === 'dark' ? 'text-gray-400' : 'text-gray-600'}>
              Sẽ mở trang đăng nhập Garena và copy thông tin tài khoản để bạn kiểm tra
            </DialogDescription>
          </DialogHeader>
          
          {selectedAccount && (
            <div className={`space-y-4 ${theme === 'dark' ? 'text-gray-300' : 'text-gray-700'}`}>
              <div className={`p-4 rounded-lg ${theme === 'dark' ? 'bg-gray-800' : 'bg-gray-50'}`}>
                <h4 className="font-semibold mb-3 text-sm uppercase tracking-wide">Thông tin đăng nhập:</h4>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className={theme === 'dark' ? 'text-gray-400' : 'text-gray-600'}>Username:</span>
                    <span className="font-mono font-semibold">{selectedAccount.username}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className={theme === 'dark' ? 'text-gray-400' : 'text-gray-600'}>Email:</span>
                    <span className="font-mono text-xs">{selectedAccount.email}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className={theme === 'dark' ? 'text-gray-400' : 'text-gray-600'}>Mật khẩu:</span>
                    <span className="font-mono font-semibold">{selectedAccount.password}</span>
                  </div>
                </div>
              </div>

              <div className={`p-3 rounded-lg ${theme === 'dark' ? 'bg-blue-900/20 border border-blue-700/30' : 'bg-blue-50 border border-blue-200'}`}>
                <p className={`text-xs ${theme === 'dark' ? 'text-blue-300' : 'text-blue-700'}`}>
                  💡 Thông tin sẽ tự động được copy vào clipboard. Bạn chỉ cần paste vào form đăng nhập.
                </p>
              </div>

              <Button 
                onClick={openGarenaLogin}
                className={`w-full cyber-button ${theme}`}
                data-testid="open-garena-login-button"
              >
                <ExternalLink className="mr-2" size={18} />
                Mở trang đăng nhập Garena
              </Button>
            </div>
          )}
        </DialogContent>
      </Dialog>

      {/* Inbox Dialog */}
      <Dialog open={inboxDialog} onOpenChange={setInboxDialog}>
        <DialogContent className={`${theme === 'dark' ? 'bg-gray-900 border-gray-700' : 'bg-white border-gray-200'} max-w-2xl`}>
          <DialogHeader>
            <DialogTitle className={`flex items-center gap-2 ${theme === 'dark' ? 'text-gray-100' : 'text-gray-900'}`}>
              <Inbox size={24} className={theme === 'dark' ? 'text-blue-400' : 'text-blue-600'} />
              Inbox Email
            </DialogTitle>
            <DialogDescription className={theme === 'dark' ? 'text-gray-400' : 'text-gray-600'}>
              {selectedAccount && `Email: ${selectedAccount.email}`}
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4 max-h-96 overflow-y-auto">
            {checkingInbox ? (
              <div className="flex items-center justify-center py-12">
                <Loader2 className={`animate-spin ${theme === 'dark' ? 'text-cyan-400' : 'text-cyan-600'}`} size={32} />
                <span className={`ml-3 ${theme === 'dark' ? 'text-gray-300' : 'text-gray-700'}`}>Đang kiểm tra inbox...</span>
              </div>
            ) : inboxMessages.length === 0 ? (
              <div className={`text-center py-12 ${theme === 'dark' ? 'text-gray-500' : 'text-gray-400'}`}>
                <Mail size={48} className="mx-auto mb-4 opacity-50" />
                <p>Inbox trống - chưa có email nào</p>
                <p className="text-sm mt-2">Email verification có thể mất vài phút để đến</p>
              </div>
            ) : (
              <div className="space-y-3">
                {inboxMessages.map((message, index) => (
                  <div 
                    key={index}
                    onClick={() => handleViewEmailContent(message)}
                    className={`p-4 rounded-lg border cursor-pointer transition-all hover:shadow-md ${theme === 'dark' ? 'bg-gray-800 border-gray-700 hover:bg-gray-750' : 'bg-gray-50 border-gray-200 hover:bg-gray-100'}`}
                  >
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex-1">
                        <div className={`font-semibold ${theme === 'dark' ? 'text-gray-200' : 'text-gray-900'}`}>
                          {message.subject || 'No Subject'}
                        </div>
                        <div className={`text-sm ${theme === 'dark' ? 'text-gray-400' : 'text-gray-600'}`}>
                          From: {typeof message.from === 'object' ? (message.from?.address || message.from?.name || 'Unknown') : (message.sender || message.from || 'Unknown')}
                        </div>
                      </div>
                      <div className={`text-xs ${theme === 'dark' ? 'text-gray-500' : 'text-gray-500'}`}>
                        {message.received || message.created_at || 'Just now'}
                      </div>
                    </div>
                    {message.intro && (
                      <div className={`text-sm mt-2 p-3 rounded ${theme === 'dark' ? 'bg-gray-900' : 'bg-white'}`}>
                        <div className={theme === 'dark' ? 'text-gray-300' : 'text-gray-700'}>
                          {message.intro.substring(0, 150)}
                          {message.intro.length > 150 && '...'}
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="flex justify-between items-center pt-4 border-t border-gray-700">
            <Button
              onClick={() => handleCheckInbox(selectedAccount)}
              variant="outline"
              size="sm"
              className={theme === 'dark' ? 'border-gray-700' : 'border-gray-300'}
              disabled={checkingInbox}
            >
              {checkingInbox ? (
                <>
                  <Loader2 className="mr-2 animate-spin" size={16} />
                  Đang tải...
                </>
              ) : (
                <>
                  <Inbox className="mr-2" size={16} />
                  Làm mới
                </>
              )}
            </Button>
            <span className={`text-xs ${theme === 'dark' ? 'text-gray-500' : 'text-gray-600'}`}>
              {inboxMessages.length} email
            </span>
          </div>
        </DialogContent>
      </Dialog>

      {/* Email Content Dialog */}
      <Dialog open={emailContentDialog} onOpenChange={setEmailContentDialog}>
        <DialogContent className={`${theme === 'dark' ? 'bg-gray-900 border-gray-700' : 'bg-white border-gray-200'} max-w-4xl max-h-[80vh]`}>
          <DialogHeader>
            <DialogTitle className={`flex items-center gap-2 ${theme === 'dark' ? 'text-gray-100' : 'text-gray-900'}`}>
              <Mail size={24} className={theme === 'dark' ? 'text-blue-400' : 'text-blue-600'} />
              Chi tiết Email
            </DialogTitle>
            {selectedEmail && (
              <DialogDescription className={theme === 'dark' ? 'text-gray-300' : 'text-gray-600'}>
                <div className="space-y-1 mt-2">
                  <div className={theme === 'dark' ? 'text-gray-200' : 'text-gray-800'}><strong>From:</strong> {typeof selectedEmail.from === 'object' ? (selectedEmail.from?.address || selectedEmail.from?.name || 'Unknown') : selectedEmail.from}</div>
                  <div className={theme === 'dark' ? 'text-gray-200' : 'text-gray-800'}><strong>Subject:</strong> {selectedEmail.subject}</div>
                  <div className={`text-xs ${theme === 'dark' ? 'text-gray-400' : 'text-gray-500'}`}>{selectedEmail.created_at}</div>
                </div>
              </DialogDescription>
            )}
          </DialogHeader>

          {loadingEmailContent ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className={`animate-spin ${theme === 'dark' ? 'text-cyan-400' : 'text-cyan-600'}`} size={32} />
              <span className={`ml-3 ${theme === 'dark' ? 'text-gray-300' : 'text-gray-700'}`}>Đang tải nội dung...</span>
            </div>
          ) : selectedEmail ? (
            <div className="space-y-4">
              {/* View Mode Toggle */}
              <div className="flex gap-2 border-b pb-3">
                <Button
                  onClick={() => setEmailViewMode('text')}
                  variant={emailViewMode === 'text' ? 'default' : 'outline'}
                  size="sm"
                  className={emailViewMode === 'text' ? 'bg-blue-600 text-white' : ''}
                >
                  Text
                </Button>
                <Button
                  onClick={() => setEmailViewMode('html')}
                  variant={emailViewMode === 'html' ? 'default' : 'outline'}
                  size="sm"
                  className={emailViewMode === 'html' ? 'bg-blue-600 text-white' : ''}
                >
                  HTML
                </Button>
              </div>

              {/* Email Content */}
              <div className={`overflow-y-auto max-h-96 p-4 rounded-lg ${theme === 'dark' ? 'bg-gray-800' : 'bg-gray-50'}`}>
                {emailViewMode === 'text' ? (
                  <div 
                    className={`whitespace-pre-wrap font-mono text-sm ${theme === 'dark' ? 'text-gray-300' : 'text-gray-700'}`}
                    style={{ 
                      wordBreak: 'break-word',
                      overflowWrap: 'break-word'
                    }}
                  >
                    {selectedEmail.text ? (
                      <div 
                        dangerouslySetInnerHTML={{
                          __html: selectedEmail.text.replace(
                            /(https?:\/\/[^\s]+)/g, 
                            '<a href="$1" target="_blank" rel="noopener noreferrer" style="text-decoration: underline; color: inherit;">$1</a>'
                          )
                        }}
                      />
                    ) : (
                      <p className={theme === 'dark' ? 'text-gray-500' : 'text-gray-400'}>Không có nội dung text</p>
                    )}
                  </div>
                ) : (
                  <div className={`prose max-w-none ${theme === 'dark' ? 'prose-invert' : ''}`}>
                    {selectedEmail.html && selectedEmail.html.length > 0 ? (
                      <iframe
                        srcDoc={selectedEmail.html[0] || selectedEmail.html}
                        className="w-full h-96 border-0"
                        title="Email HTML Content"
                        sandbox="allow-same-origin"
                      />
                    ) : (
                      <p className={theme === 'dark' ? 'text-gray-500' : 'text-gray-400'}>Không có nội dung HTML</p>
                    )}
                  </div>
                )}
              </div>

              {/* Attachments */}
              {selectedEmail.attachments && selectedEmail.attachments.length > 0 && (
                <div className={`p-3 rounded-lg ${theme === 'dark' ? 'bg-gray-800' : 'bg-gray-50'}`}>
                  <h4 className={`font-semibold mb-2 ${theme === 'dark' ? 'text-gray-200' : 'text-gray-900'}`}>
                    Đính kèm ({selectedEmail.attachments.length})
                  </h4>
                  <div className="space-y-1">
                    {selectedEmail.attachments.map((att, idx) => (
                      <div key={idx} className={`text-sm ${theme === 'dark' ? 'text-gray-400' : 'text-gray-600'}`}>
                        📎 {att.filename || `Attachment ${idx + 1}`}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className={`text-center py-12 ${theme === 'dark' ? 'text-gray-500' : 'text-gray-400'}`}>
              <p>Không thể tải nội dung email</p>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default Dashboard;