// app/static/app.js
const form = document.querySelector("#design-form");
const modelSelect = document.querySelector("#model");
const submitButton = document.querySelector("#submit-button");
const resultEmpty = document.querySelector("#result-empty");
const resultContent = document.querySelector("#result-content");
const resultText = document.querySelector("#result-text");
const resultTitle = document.querySelector("#result-title");
const resultModel = document.querySelector("#result-model");
const toast = document.querySelector("#toast");

function showToast(message) {
  toast.textContent = message;
  toast.classList.add("visible");
  window.setTimeout(() => toast.classList.remove("visible"), 3200);
}

async function loadModels() {
  const refreshButton = document.querySelector("#refresh-models");
  refreshButton.disabled = true;
  refreshButton.textContent = "جارٍ التحديث…";

  try {
    const response = await fetch("/api/models");
    const payload = await response.json();

    if (!response.ok) {
      throw new Error(payload.detail || "تعذر تحميل النماذج.");
    }

    const previousValue = modelSelect.value;
    modelSelect.innerHTML = '<option value="">النموذج الافتراضي</option>';

    for (const model of payload.data || []) {
      const option = document.createElement("option");
      option.value = model.id;
      option.textContent = model.name;
      modelSelect.append(option);
    }

    if ([...modelSelect.options].some((option) => option.value === previousValue)) {
      modelSelect.value = previousValue;
    }

    showToast("تم تحديث قائمة النماذج.");
  } catch (error) {
    showToast(error.message);
  } finally {
    refreshButton.disabled = false;
    refreshButton.textContent = "تحديث النماذج";
  }
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  const formData = new FormData(form);
  const payload = {
    brand_name: formData.get("brand_name").trim(),
    industry: formData.get("industry").trim(),
    product: formData.get("product").trim(),
    audience: formData.get("audience").trim(),
    style: formData.get("style").trim(),
    deliverables: formData.getAll("deliverables"),
    model: formData.get("model") || null,
  };

  submitButton.disabled = true;
  submitButton.innerHTML = "<span>جارٍ إعداد المقترح…</span><span>◌</span>";
  resultEmpty.classList.add("hidden");
  resultContent.classList.add("hidden");

  try {
    const response = await fetch("/api/design", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify(payload),
    });

    const result = await response.json();
    if (!response.ok) {
      throw new Error(result.detail || "تعذر إنشاء المقترح.");
    }

    resultTitle.textContent = payload.brand_name;
    resultText.textContent = result.design;
    resultModel.textContent = `النموذج المستخدم: ${result.model}`;
    resultContent.classList.remove("hidden");
  } catch (error) {
    resultEmpty.classList.remove("hidden");
    showToast(error.message);
  } finally {
    submitButton.disabled = false;
    submitButton.innerHTML = "<span>إنشاء التوجه الإبداعي</span><span aria-hidden=\"true\">←</span>";
  }
});

document.querySelector("#refresh-models").addEventListener("click", loadModels);

document.querySelector("#copy-button").addEventListener("click", async () => {
  try {
    await navigator.clipboard.writeText(resultText.textContent);
    showToast("تم نسخ المقترح.");
  } catch {
    showToast("تعذر النسخ من المتصفح.");
  }
});
