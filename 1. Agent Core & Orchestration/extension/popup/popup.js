// 팝업: on/off 토글 및 사용자 ID 수동 설정을 chrome.storage에 저장한다.
const checkbox = document.getElementById("enabled");
const label = document.getElementById("toggleLabel");
const status = document.getElementById("status");
const userIdInput = document.getElementById("userIdInput");
const saveIdBtn = document.getElementById("saveIdBtn");
const syncStatus = document.getElementById("syncStatus");

function render(enabled) {
  checkbox.checked = enabled;
  label.textContent = enabled ? "켜짐" : "꺼짐";
  status.textContent = enabled ? "읽는 글을 모니터링하는 중…" : "";
}

(async () => {
  const { enabled = false, userId = "" } = await chrome.storage.local.get(["enabled", "userId"]);
  render(enabled);
  userIdInput.value = userId;
  if (userId) {
    syncStatus.textContent = `연동된 ID: ${userId}`;
    syncStatus.style.color = "#00b894";
  } else {
    syncStatus.textContent = "연동된 사용자 ID가 없습니다.";
    syncStatus.style.color = "#d63031";
  }
})();

checkbox.addEventListener("change", async () => {
  const enabled = checkbox.checked;
  await chrome.storage.local.set({ enabled });
  render(enabled);
});

saveIdBtn.addEventListener("click", async () => {
  const newId = userIdInput.value.trim();
  if (newId) {
    await chrome.storage.local.set({ userId: newId });
    syncStatus.textContent = `연동 완료: ${newId}`;
    syncStatus.style.color = "#00b894";
  } else {
    await chrome.storage.local.remove("userId");
    syncStatus.textContent = "연동 해제됨 (랜덤 UUID 사용)";
    syncStatus.style.color = "#d63031";
  }
});

// 로컬 PDF: pdf.js 뷰어를 새 탭으로 연다
document.getElementById("openPdf").addEventListener("click", () => {
  chrome.tabs.create({ url: chrome.runtime.getURL("pdf/viewer.html") });
});
