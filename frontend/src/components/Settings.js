import React, { useState, useEffect } from 'react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from './ui/dialog';
import { toast } from 'sonner';
import { Settings as SettingsIcon } from 'lucide-react';

const Settings = ({ open, onOpenChange }) => {
  // Default API key provided with the app
  const DEFAULT_API_KEY = 'TZvExfsiaNZBBfi3z047GsrfUEgNRWp3';
  
  const [mongoUrl, setMongoUrl] = useState('');
  const [apiKey, setApiKey] = useState(DEFAULT_API_KEY);
  const [dbName, setDbName] = useState('garena_creator_db');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (open && window.electron) {
      loadSettings();
    }
  }, [open]);

  const loadSettings = async () => {
    try {
      if (window.electron) {
        const settings = await window.electron.getSettings();
        setMongoUrl(settings.mongoUrl || '');
        // Use saved API key if exists, otherwise use default
        setApiKey(settings.apiKey || DEFAULT_API_KEY);
        setDbName(settings.dbName || 'garena_creator_db');
      }
    } catch (error) {
      console.error('Failed to load settings:', error);
      toast.error('Không thể tải cài đặt');
    }
  };

  const handleSave = async () => {
    setLoading(true);
    try {
      if (window.electron) {
        const result = await window.electron.saveSettings({
          mongoUrl,
          apiKey,
          dbName,
        });

        if (result.success) {
          toast.success('Cài đặt đã được lưu! Khởi động lại ứng dụng để áp dụng.');
          onOpenChange(false);
        } else {
          toast.error('Không thể lưu cài đặt: ' + result.error);
        }
      } else {
        // Web mode - save to localStorage
        localStorage.setItem('mongoUrl', mongoUrl);
        localStorage.setItem('apiKey', apiKey);
        localStorage.setItem('dbName', dbName);
        toast.success('Cài đặt đã được lưu!');
        onOpenChange(false);
      }
    } catch (error) {
      console.error('Failed to save settings:', error);
      toast.error('Không thể lưu cài đặt');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <SettingsIcon className="w-5 h-5" />
            Cài Đặt Ứng Dụng
          </DialogTitle>
          <DialogDescription>
            Cấu hình kết nối database và API keys cho ứng dụng.
          </DialogDescription>
        </DialogHeader>
        <div className="grid gap-4 py-4">
          <div className="grid gap-2">
            <Label htmlFor="mongoUrl">MongoDB Connection URL</Label>
            <Input
              id="mongoUrl"
              placeholder="mongodb://localhost:27017 hoặc mongodb+srv://..."
              value={mongoUrl}
              onChange={(e) => setMongoUrl(e.target.value)}
              type="text"
            />
            <p className="text-sm text-muted-foreground">
              URL kết nối đến MongoDB database (local hoặc cloud)
            </p>
          </div>
          <div className="grid gap-2">
            <Label htmlFor="dbName">Database Name</Label>
            <Input
              id="dbName"
              placeholder="garena_creator_db"
              value={dbName}
              onChange={(e) => setDbName(e.target.value)}
              type="text"
            />
            <p className="text-sm text-muted-foreground">
              Tên database sẽ được sử dụng
            </p>
          </div>
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 text-sm mb-2">
            <p className="font-semibold text-blue-900 mb-1">ℹ️ Dịch vụ Email Tạm:</p>
            <ul className="text-blue-800 space-y-1 ml-4 list-disc">
              <li><strong>Mail.tm:</strong> Miễn phí, không cần API key (mặc định)</li>
              <li><strong>10MinuteMail:</strong> Miễn phí, không cần API key</li>
              <li><strong>TempMail API:</strong> Sử dụng API key đã cung cấp sẵn</li>
            </ul>
            <p className="text-blue-700 mt-2 text-xs">
              → App sẽ tự động chuyển đổi giữa các dịch vụ để đảm bảo hoạt động tốt nhất
            </p>
          </div>
          <div className="grid gap-2">
            <Label htmlFor="apiKey">
              Temp Mail API Key 
              <span className="ml-2 text-xs text-green-600 font-semibold">
                ✓ Đã cung cấp sẵn
              </span>
            </Label>
            <Input
              id="apiKey"
              placeholder="Đã có API key mặc định"
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              type="password"
            />
            <p className="text-sm text-muted-foreground">
              API key đã được tích hợp sẵn, bạn không cần thay đổi.
              <br />
              <span className="text-green-600">
                ✓ Có thể sử dụng ngay mà không cần cấu hình
              </span>
            </p>
          </div>
          <div className="bg-amber-50 border border-amber-200 rounded-lg p-3 text-sm">
            <p className="font-semibold text-amber-900 mb-1">⚠️ Lưu ý:</p>
            <p className="text-amber-800">
              Sau khi lưu cài đặt, bạn cần khởi động lại ứng dụng để các thay đổi có hiệu lực.
            </p>
          </div>
        </div>
        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)} disabled={loading}>
            Hủy
          </Button>
          <Button onClick={handleSave} disabled={loading}>
            {loading ? 'Đang lưu...' : 'Lưu Cài Đặt'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

export default Settings;