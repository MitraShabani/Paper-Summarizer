// document.getElementById("uploadButton").onclick = async () => {
//   const file = document.getElementById("pdfInput").files[0];
//   if (!file) return;

//   const formData = new FormData();
//   formData.append("file", file);

//   const response = await fetch("http://127.0.0.1:8000/parse", {
//     method: "POST",
//     body: formData
//   });

//   const data = await response.json();
//   document.getElementById("output").textContent = JSON.stringify(data, null, 2);
// };
