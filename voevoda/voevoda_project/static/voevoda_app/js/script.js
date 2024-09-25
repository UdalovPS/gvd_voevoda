document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('access_code_form').addEventListener('submit', function(event) {
        event.preventDefault(); // Предотвращаем отправку формы
        generateAccessCode();
    });

    document.getElementById('validate_code_form').addEventListener('submit', function(event) {
        event.preventDefault(); // Предотвращаем отправку формы
        validateAccessCode();
    });
});

async function generateAccessCode() {
    const name = document.getElementById('name').value;
    console.log(`name: ${name}`);
    const url = "http://127.0.0.1:8000/api/keys/";
    const params = {
        "sub_key": "render",
        "name": name
    };
    const fullUrl = url + '?' + new URLSearchParams(params);
    console.log(fullUrl); // Выводим полный URL с параметрами
    try {
        const response = await fetch(fullUrl, {
            method: "GET",
            headers: {
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
        });

        if (!response.ok) {
            alert("Invalid name");
            throw new Error('Network response was not ok');
        }

        const result = await response.json();
        if (result.success) {
            alert(result.data);
            document.getElementById('access_code_form').style.display = 'none';
            document.getElementById('validate_code_form').style.display = 'block';
        }

    } catch (error) {
        console.error('Error:', error);
    }
};

async function validateAccessCode() {
    const code = document.getElementById('code').value;
    console.log(`code: ${code}`);
    const url = "http://127.0.0.1:8000/api/keys/";
    const payload = {
        "code": code
    };
    try {
        const response = await fetch(url, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            alert("Invalid code");
            throw new Error('Network response was not ok');
        }

        const result = await response.json();
        if (result.success) {
            console.log(`redirect`);
            window.location.href = "http://127.0.0.1:8000/?code=" + encodeURIComponent(code);
        }

    } catch (error) {
        console.error('Error:', error);
    }
};
