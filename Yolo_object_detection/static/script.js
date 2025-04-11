document.querySelector('form').onsubmit = async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    const response = await fetch('/predict', {
        method: 'POST',
        body: formData
    });
    const data = await response.json();
    const resultDiv = document.getElementById('result');
    resultDiv.innerHTML = '<h2>Processed Image:</h2>';
    resultDiv.innerHTML += '<img src="/output_image" alt="Processed Image">';
};
document.querySelector('form').onsubmit = async (e) => {
    e.preventDefault();
    
    const resultDiv = document.getElementById('result');
    resultDiv.innerHTML = ''; // Xóa nội dung cũ trước khi hiển thị kết quả mới

    const formData = new FormData(e.target);
    const response = await fetch('/predict', {
        method: 'POST',
        body: formData
    });
    const data = await response.json();
    
    // Thêm tham số ngẫu nhiên vào URL hình ảnh để tránh cache
    const imageUrl = `/output_image?rand=${new Date().getTime()}`;
    
    resultDiv.innerHTML = '<h2>Processed Image:</h2>';
    resultDiv.innerHTML += `<img src="${imageUrl}" alt="Processed Image">`;
};
document.querySelector('input[type="file"]').addEventListener('change', function(event) {
    const file = event.target.files[0];
    const reader = new FileReader();
    
    reader.onload = function(e) {
        const img = document.createElement('img');
        img.src = e.target.result;
        img.alt = 'Uploaded Image';
        
        const resultDiv = document.getElementById('result');
        resultDiv.innerHTML = ''; // Xóa nội dung cũ
        resultDiv.appendChild(img); // Thêm ảnh đã tải lên
    }
    
    if (file) {
        reader.readAsDataURL(file); // Đọc ảnh như là URL dữ liệu
    }
});