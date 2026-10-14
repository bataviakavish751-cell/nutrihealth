function startScan() {
    fetch('/scan/')
        .then(res => res.json())
        .then(data => {
            document.getElementById('result').textContent =
                JSON.stringify(data, null, 2);
        })
        .catch(err => alert("Error scanning barcode"));
}
