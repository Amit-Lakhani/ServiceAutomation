document.addEventListener("DOMContentLoaded", async () => {
    const urlParams = new URLSearchParams(window.location.search);
    const tool = urlParams.get("tool");
    const form = document.getElementById("dynamicForm");
    const resultDiv = document.getElementById("result");
    const title = document.getElementById("tool-title");

    if (!tool) {
        title.textContent = "No tool specified.";
        return;
    }

    const res = await fetch("/api/services");
    const services = await res.json();
    const config = services[tool];

    console.log("[Loaded Config]:", config);

    if (!config) {
        title.textContent = "Tool not found.";
        return;
    }

    title.textContent = config.name;
    form.innerHTML = ""; // Clear previous fields

    // Build form inputs
    config.fields.forEach(field => {
        const fieldElement = createInputField(field);
        form.appendChild(fieldElement);
    });

    // Create submit button
    const submitBtn = document.createElement("button");
    submitBtn.type = "submit";
    submitBtn.textContent = "Submit";
    submitBtn.className = "bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700";
    form.appendChild(submitBtn);

    // Submit handler
    form.addEventListener("submit", async (e) => {
        e.preventDefault();  // Always prevent default immediately

        submitBtn.disabled = true;
        submitBtn.textContent = "Processing...";

        const formData = new FormData(form);
        const response = await fetch(config.endpoint, {
            method: "POST",
            body: formData
        });

        if (response.ok) {
            if (config.response.type === "file") {
                const blob = await response.blob();
                const downloadUrl = URL.createObjectURL(blob);

                // Extract filename from Content-Disposition header
                const contentDisposition = response.headers.get("Content-Disposition");
                let downloadName = "output.zip"; // fallback name
                if (contentDisposition) {
                    const fileNameMatch = contentDisposition.match(/filename="?([^"]+)"?/);
                    if (fileNameMatch && fileNameMatch[1]) {
                        downloadName = fileNameMatch[1];
                    }
                }

                const a = document.createElement("a");
                a.href = downloadUrl;
                a.download = downloadName;
                document.body.appendChild(a);
                a.click();
                a.remove();
                URL.revokeObjectURL(downloadUrl);

                resultDiv.textContent = "Download started...";

            } else if (config.response.type === "text") {
                const text = await response.text();
                resultDiv.textContent = text;
            } else {
                const text = await response.text();
                resultDiv.textContent = text;
            }
        } else {
            const text = await response.text();
            resultDiv.textContent = "Error: " + text;
        }

        submitBtn.disabled = false;
        submitBtn.textContent = "Submit";

    });

});

// COMPONENT BUILDERS

function createInputField(field) {
    const wrapper = document.createElement("div");

    const label = document.createElement("label");
    label.className = "block text-sm font-medium mb-1";
    label.textContent = field.label;
    wrapper.appendChild(label);

    let input;
    switch (field.type) {
        case "text":
            input = createTextInput(field);
            break;
        case "number":
            input = createNumberInput(field);
            break;
        case "file":
            input = createFileInput(field);
            break;
        case "textarea":
            input = createTextarea(field);
            break;
        case "checkbox":
            input = createCheckbox(field);
            break;
        case "radio":
            input = createRadio(field);
            break;
        default:
            input = createTextInput(field);
    }

    wrapper.appendChild(input);
    return wrapper;
}

function createTextInput(field) {
    const input = document.createElement("input");
    input.type = "text";
    input.name = field.name;
    input.className = "w-full border p-2 rounded";
    if (field.required) input.required = true;
    return input;
}

function createNumberInput(field) {
    const input = document.createElement("input");
    input.type = "number";
    input.name = field.name;
    input.className = "w-full border p-2 rounded";
    if (field.required) input.required = true;
    return input;
}

function createFileInput(field) {
    const wrapper = document.createElement("div");

    const input = document.createElement("input");
    input.type = "file";
    input.name = field.name;
    input.className = "w-full border p-2 rounded";
    if (field.required) input.required = true;
    if (field.multiple) input.multiple = true;

    const fileListDisplay = document.createElement("ul");
    fileListDisplay.className = "mt-2 text-sm text-gray-700 list-disc list-inside";

    input.addEventListener("change", () => {
        fileListDisplay.innerHTML = "";  // Clear previous
        Array.from(input.files).forEach(file => {
            const li = document.createElement("li");
            li.textContent = file.name;
            fileListDisplay.appendChild(li);
        });
    });

    wrapper.appendChild(input);
    wrapper.appendChild(fileListDisplay);
    return wrapper;
}

function createTextarea(field) {
    const textarea = document.createElement("textarea");
    textarea.name = field.name;
    textarea.className = "w-full border p-2 rounded h-40 resize-y";
    textarea.style.minHeight = "400px";  // increase height here
    if (field.required) textarea.required = true;
    return textarea;
}

function createCheckbox(field) {
    const input = document.createElement("input");
    input.type = "checkbox";
    input.name = field.name;
    if (field.required) input.required = true;
    return input;
}

function createRadio(field) {
    // Expand later for group radio buttons if needed
    const input = document.createElement("input");
    input.type = "radio";
    input.name = field.name;
    if (field.required) input.required = true;
    return input;
}
