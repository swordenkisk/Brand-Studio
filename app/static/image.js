// app/static/image.js
const form = document.querySelector("#image-form");
const modelSelect = document.querySelector("#image-model");
const submitButton = document.querySelector("#image-submit");
const emptyState = document.querySelector("#image-empty");
const resultBox = document.querySelector("#image-result");
const imageElement = document.querySelector("#generated-image");
const downloadLink = document.querySelector("#download-image");
const imageMeta = document.querySelector("#image-meta");
const toast = document.querySelector("#toast");

function showToast(message) {
  toast.textContent = message;
  toast.classList.add("visible");
  window.setTimeout(() => toast.classList.remove("visible"), 3500);
}

async function loadImageModels() {
  try {
    const response = await fetch("/api/image-models");
    const payload = await response.json();

    if (!response.ok) {
      throw new Error(payload.detail || "تعذر تحميل نماذج الصور.");
    }

    modelSelect.replaceChildren();
    for (const model of payload.data || []) {
      const option = document.createElement("option");
      option.value = model.id;
      option.textContent = model.name;
      modelSelect.append(option);
    }

    if (!modelSelect.options.length) {
      throw new Error("لم يتم العثور على نماذج صور متاحة.");
    }
  } catch (error) {
    modelSelect.innerHTML = '<option value="">تعذر تحميل النماذج</option>';
    showToast(error.message);
  }
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  const payload = {
    prompt: document.querySelector("#prompt").value.trim(),
    model: modelSelect.value,
    aspect_ratio: document.querySelector("#aspect-ratio").value,
    resolution: document.querySelector("#resolution").value,
  };

  if (!payload.model) {
    showToast("اختر نموذجاً صالحاً للصور.");
    return;
  }

  submitButton.disabled = true;
  submitButton.innerHTML = "<span>جارٍ إنشاء الصورة…</span><span>◌</span>";
  emptyState.classList.add("hidden");
  resultBox.classList.add("hidden");

  try {
    const response = await fetch("/api/images", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify(payload),
    });
    const result = await response.json();

    if (!response.ok) {
      throw new Error(result.detail || "تعذر إنشاء الصورة.");
    }

    imageElement.src = result.image_url;
    downloadLink.href = result.image_url;
    imageMeta.textContent = `النموذج: ${result.model}`;
    resultBox.classList.remove("hidden");
  } catch (error) {
    emptyState.classList.remove("hidden");
    showToast(error.message);
  } finally {
    submitButton.disabled = false;
    submitButton.innerHTML = "<span>إنشاء الصورة</span><span aria-hidden=\"true\">←</span>";
  }
});

loadImageModels();
