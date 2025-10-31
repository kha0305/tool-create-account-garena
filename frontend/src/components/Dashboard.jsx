import { useState, useEffect } from 'react';
import axios from 'axios';
import { toast } from 'sonner';
import { Loader2, Trash2, Download, Zap, Database, Sun, Moon, ExternalLink, CheckCircle2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Progress } from '@/components/ui/progress';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const Dashboard = () => {
  const [quantity, setQuantity] = useState('5');
  const [creating, setCreating] = useState(false);
  const [currentJob, setCurrentJob] = useState(null);
  const [accounts, setAccounts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [stats, setStats] = useState({ total: 0, created: 0 });
  const [theme, setTheme] = useState(() => {
    return localStorage.getItem('theme') || 'dark';
  });

  // Quantity options
  const quantities = [1, 5, 10, 15, 20, 25, 30, 40, 50, 60, 70, 80, 90, 100];

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

    setCreating(true);
    try {
      const response = await axios.post(`${API}/accounts/create`, {
        quantity: parseInt(quantity)
      });

      toast.success(`Đã bắt đầu tạo ${quantity} tài khoản`);
      pollJobStatus(response.data.job_id);
    } catch (error) {
      toast.error('Lỗi khi tạo tài khoản');
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

  // Export to CSV
  const handleExportCSV = () => {
    if (accounts.length === 0) {
      toast.error('Không có tài khoản để xuất');
      return;
    }

    const headers = ['Username', 'Email', 'Phone', 'Password', 'Status', 'Created At'];
    const rows = accounts.map(acc => [
      acc.username,
      acc.email,
      acc.phone,
      acc.password,
      acc.status,
      new Date(acc.created_at).toLocaleString('vi-VN')
    ]);

    const csvContent = [
      headers.join(','),
      ...rows.map(row => row.map(cell => `"${cell}"`).join(','))
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = `garena_accounts_${Date.now()}.csv`;
    link.click();
    toast.success('Đã xuất file CSV');
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
      >
        {theme === 'dark' ? (
          <>
            <Sun size={20} />
            <span>Sáng</span>
          </>
        ) : (
          <>
            <Moon size={20} />
            <span>Tối</span>
          </>
        )}
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
            <div className="flex flex-col md:flex-row gap-4 items-end">
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
              <Button
                onClick={handleCreateAccounts}
                disabled={creating}
                className={`cyber-button ${theme} h-10 min-w-[200px]`}
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
                <Button
                  onClick={handleExportCSV}
                  variant="outline"
                  size="sm"
                  className={theme === 'dark' ? 'bg-green-900/20 hover:bg-green-900/40 border-green-700 text-green-400' : 'bg-green-50 hover:bg-green-100 border-green-300 text-green-700'}
                  disabled={accounts.length === 0}
                  data-testid="export-csv-button"
                >
                  <Download className="mr-2" size={16} />
                  Xuất CSV
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
                      <th>Số điện thoại</th>
                      <th>Mật khẩu</th>
                      <th>Trạng thái</th>
                      <th>Ngày tạo</th>
                      <th>Thao tác</th>
                    </tr>
                  </thead>
                  <tbody>
                    {accounts.map((account, index) => (
                      <tr key={account.id} data-testid={`account-row-${index}`}>
                        <td className={`font-semibold ${theme === 'dark' ? 'text-cyan-400' : 'text-cyan-700'}`} data-testid={`account-username-${index}`}>{account.username}</td>
                        <td className="text-sm" data-testid={`account-email-${index}`}>{account.email}</td>
                        <td className="text-sm" data-testid={`account-phone-${index}`}>{account.phone}</td>
                        <td className="text-sm font-mono" data-testid={`account-password-${index}`}>{account.password}</td>
                        <td>
                          <span className={`status-badge status-${account.status} ${theme}`} data-testid={`account-status-${index}`}>
                            {account.status}
                          </span>
                        </td>
                        <td className="text-sm" data-testid={`account-created-${index}`}>
                          {new Date(account.created_at).toLocaleString('vi-VN')}
                        </td>
                        <td>
                          <Button
                            onClick={() => handleDeleteAccount(account.id)}
                            variant="ghost"
                            size="sm"
                            className={theme === 'dark' ? 'text-red-400 hover:text-red-300 hover:bg-red-900/20' : 'text-red-600 hover:text-red-700 hover:bg-red-50'}
                            data-testid={`delete-account-button-${index}`}
                          >
                            <Trash2 size={16} />
                          </Button>
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
    </div>
  );
};

export default Dashboard;