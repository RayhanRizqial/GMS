let models = [
  
];  // Ubah dari data dummy ke array kosong

// Fungsi untuk mengambil data dari API FastAPI
async function fetchModels() {
  try {
    const response = await fetch("/api/models");
    const data = await response.json();
    models = data.map(model => ({
      model_id: model.id, // Ubah sesuai dengan kolom 'id' yang ada di database
      tanggalFineTune: model.tanggal,
      instruksiModel: model.Instruksi,
      namaModelFineTune: model.namaModel,
      fineTuningVersion: model.verFine_tuning,
      temp: model.temp
    }));
    displayModels(models);  // Cetak ulang models setelah di-fetch
  } catch (error) {
    console.error("Error fetching models:", error);
  }
}


// Panggil fungsi fetchModels saat halaman pertama kali dimuat
fetchModels();


// Fungsi untuk mencetak model ke dalam HTML
// Fungsi untuk mencetak model ke dalam HTML
function displayModels(filteredModels) {
  const modelListContainer = document.getElementById('modelListContainer');
  modelListContainer.innerHTML = ''; // Bersihkan kontainer sebelum mencetak ulang

  if (filteredModels.length === 0) {
    // Jika tidak ada model yang cocok, tampilkan pesan "Model tidak ditemukan"
    const noModelElement = document.createElement('div');
    noModelElement.classList.add('noModelFound');
    noModelElement.innerHTML = `
      <div class="modelDesc">Model tidak ditemukan
      </div>
    `;
    modelListContainer.appendChild(noModelElement);
    return;
  }

  filteredModels.forEach(model => {
    // Buat elemen untuk setiap model
    const modelElement = document.createElement('div');
    modelElement.classList.add('modelList');

    modelElement.innerHTML = `
      <div class="modelDesc">
        <div class="desc">${model.namaModelFineTune}</div>
        <div class="tag">
          <div class="model-tag">${model.fineTuningVersion}</div>
          <div class="model-tag">${model.tanggalFineTune}</div>
        </div>
      </div>
      <div class="tombolCongfig">
        <button type="button" onclick="window.location.href='/model-config-set?id=${model.model_id}'">Configure</button>
      </div>
    `;

    // Tambahkan elemen model ke container
    modelListContainer.appendChild(modelElement);
  });
}


// Fungsi untuk filter model berdasarkan input pencarian
function filterModels() {
  const searchInput = document.getElementById('searchInput').value.toLowerCase();
  
  if (searchInput.length >= 3) { // Minimum 3 karakter untuk memulai pencarian
    const filteredModels = models.filter(model => 
      model.namaModelFineTune.toLowerCase().includes(searchInput)
    );
    displayModels(filteredModels);
  } else {
    displayModels(models); // Jika kurang dari 3 huruf, tampilkan semua
  }
}

// Event listener untuk input pencarian
document.getElementById('searchInput').addEventListener('input', filterModels);

// Cetak semua model saat halaman pertama kali dimuat
displayModels(models);





// Config set
// Fungsi untuk memperbarui nilai slider
function updateSliderValue() {
  const slider = document.getElementById("fineTuneSlider");
  const valueDisplay = document.getElementById("sliderValue");
  valueDisplay.textContent = slider.value;
}

// Fungsi untuk memeriksa apakah ada perubahan data
function checkChanges() {
  const namaModel = document.getElementById("namaModel").value;
  const instruksiModel = document.getElementById("instruksiModel").value;
  const fineTuningVersion = document.getElementById("fineTuningVersion").value;
  const fineTuningSlider = document.getElementById("fineTuneSlider").value;

  const isChanged = namaModel !== "Model Pembaca Jenis Pertanyaan" ||
                    instruksiModel !== "Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s" ||
                    fineTuningVersion !== "v1" ||
                    fineTuningSlider !== "1";

  const saveBtn = document.getElementById("saveBtn");
  const cancelBtn = document.getElementById("cancelBtn");

  if (isChanged) {
    saveBtn.disabled = false;
    cancelBtn.disabled = false;
    saveBtn.classList.remove("disabled");
    cancelBtn.classList.remove("disabled");
  } else {
    saveBtn.disabled = true;
    cancelBtn.disabled = true;
    saveBtn.classList.add("disabled");
    cancelBtn.classList.add("disabled");
  }
}


