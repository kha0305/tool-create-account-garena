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
  const [mongoUrl, setMongoUrl] = useState('');
  const [apiKey, setApiKey] = useState('');
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
        setApiKey(settings.apiKey || '');
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
            <Label htmlFor="apiKey">Temp Mail API Key (Optional)</Label>
            <Input
              id="apiKey"
              placeholder="API key từ apilayer.com"
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              type="password"
            />
            <p className="text-sm text-muted-foreground">
              API key cho dịch vụ email tạm (nếu cần)
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