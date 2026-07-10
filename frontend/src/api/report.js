import apiClient from "./client";

export const downloadMonthlyReport = async (month, year, format) => {
  const response = await apiClient.get("/report/monthly", {
    params: { month, year, format },
    responseType: "blob",
    timeout: 30000,
  });
  const url = URL.createObjectURL(response.data);
  const link = document.createElement("a");
  link.href = url;
  link.download = `rapport-noc-${year}-${String(month).padStart(2, "0")}.${format}`;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
};
