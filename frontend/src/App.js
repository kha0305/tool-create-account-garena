import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8001";

// Hàm gọi API tạo tài khoản
export async function createAccounts(quantity, emailProvider = "mail.tm") {
  return axios.post(
    `${API_BASE_URL}/api/accounts/create`,
    {
      quantity: Number(quantity),
      email_provider: emailProvider
    },
    {
      headers: {
        "Content-Type": "application/json"
      }
    }
  );
}

// Hàm lấy danh sách tài khoản
export async function getAccounts() {
  return axios.get(`${API_BASE_URL}/api/accounts`);
}
