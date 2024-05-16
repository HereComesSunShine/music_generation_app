document.addEventListener('DOMContentLoaded', () => {
    const uploadForm = document.getElementById('uploadForm');
    const generateButton = document.getElementById('generateButton');
    const downloadButton = document.getElementById('downloadButton');
    const generatedMusic = document.getElementById('generatedMusic');
    const inputMidi = document.getElementById('midiFile')
    const midiplayer = document.getElementById('midi-player');
    const loadingAnimation = document.getElementById('loadingAnimation');
    const uploadButton = document.getElementById('uploadbutton')
    
    const compositionLengthInput = document.getElementById('compositionLength');
    const compositionValueOutput = document.getElementById('compositionValue');

    compositionLengthInput.addEventListener('input', function() {
        compositionValueOutput.textContent = "Composition Length: " + this.value;
    });

    uploadButton.addEventListener('click',(event)  => {
        event.preventDefault()

        inputMidi.style.display= "block"
    })    
    
    generateButton.addEventListener('click', () => {
        loadingAnimation.style.display = 'block'; // Показываем анимацию загрузки

        // Получаем файл из input[type="file"]
        //const midiFile = document.getElementById('midiFile').files[0];
        const midiFile = inputMidi.files[0]
        // Создаем объект FormData и добавляем в него файл
        const formData = new FormData();
        formData.append('midiFile', midiFile);

        // Получаем остальные данные для генерации музыки
        const instrument = document.getElementById('instrument').value;
        const style = document.getElementById('style').value;
        const compositionLength = document.getElementById('compositionLength').value;
        const randswitch = document.getElementById('switch').checked;
        if (compositionLength < 50) {
            alert('Composition length must be at least 50');
            return;
        }
        if (compositionLength > 500) {
            alert('Composition length must be lower than 500');
            return;
        }

        // Добавляем остальные данные в объект FormData
        formData.append('instrument', instrument);
        formData.append('style', style);
        formData.append('compositionLength', compositionLength);
        formData.append('random',randswitch);
        // Отправляем FormData на сервер для генерации музыки
        fetch('/generate_music', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            // Обработка ответа от сервера
            generatedMusic.textContent = data.filename; // Отображаем сообщение об успешной генерации музыки
            downloadButton.setAttribute('data-filename', data.filename); // Сохраняем имя сгенерированного файла для кнопки загрузки
            downloadButton.style.display = 'block'; // Показываем кнопку загрузки
            midiplayer.style.display = 'block';
            
            midiplayer.src="http://localhost:5000/generated/"+data.filename
            loadingAnimation.style.display = 'none'; // Скрываем анимацию загрузки
        })
        .catch(error  => {
            console.error('Error generating music:', error);
            // Обработка ошибок
            alert('Error generating music. Please try again later.');
            loadingAnimation.style.display = 'none'; // Скрываем анимацию загрузки
        });
    });

    downloadButton.addEventListener('click', () => {
        const filename = downloadButton.getAttribute('data-filename');
        fetch(`/download_generated/${filename}`)
        .then(response => response.blob())
        .then(blob => {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
        });
    });
});
