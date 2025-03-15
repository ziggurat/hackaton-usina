import { useState, useRef } from "react";
import micImage from '../assets/mic.svg'
import "./Recorder.css";

const Recorder = ()=>{
  const [recording, setRecording] = useState(false);
  const mediaRecorder = useRef(null);
  const audioChunks = useRef([]);

  // Iniciar la grabación cuando el usuario presiona el botón
  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorder.current = new MediaRecorder(stream);

      mediaRecorder.current.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunks.current.push(event.data);
        }
      };

      mediaRecorder.current.onstop = () => {
        const audioBlob = new Blob(audioChunks.current, { type: "audio/mp3" });
        const url = URL.createObjectURL(audioBlob);
        autoDownload(url); // Llamamos la función para descargar automáticamente
        audioChunks.current = []; // Limpiar buffer
      };

      mediaRecorder.current.start();
      setRecording(true);
    } catch (error) {
      console.error("Error al acceder al micrófono:", error);
    }
  };

  // Detener la grabación cuando el usuario suelta el botón
  const stopRecording = () => {
    if (mediaRecorder.current && mediaRecorder.current.state !== "inactive") {
      mediaRecorder.current.stop();
      setRecording(false);
    }
  };

  // Función para descargar automáticamente el archivo
  const autoDownload = (url) => {
    const a = document.createElement("a");
    a.href = url;
    a.download = "grabacion.mp3";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  };

    return (
        <div className="recorder">
          <button className='mic'
            onMouseDown={startRecording}
            onMouseUp={stopRecording}
            onTouchStart={startRecording}
            onTouchEnd={stopRecording}
          >
            <img src={ micImage } alt="Grabar una pregunta" />
          </button>
          <span>
            {recording ? "Grabando..." : "Mantén presionado"}
          </span>
    
        </div>
      );
}

export default Recorder


// className={`px-4 py-2 rounded-full ${
//   recording ? "bg-red-500" : "bg-blue-500"
// } text-white`}