import { useState, useRef } from "react";
import micImage from '../assets/mic.svg'
import "./Recorder.css";

const Recorder = ({ onAudioRecorded, onRecord }) =>{
  const [isRecording, setIsRecording] = useState(false);
  const mediaRecorder = useRef(null);
  const audioChunks = useRef([]);

  // Iniciar la grabación cuando el usuario presiona el botón
  const startRecording = async () => {
    try {
      onRecord();
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorder.current = new MediaRecorder(stream);

      mediaRecorder.current.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunks.current.push(event.data);
        }
      };

      mediaRecorder.current.onstop = () => {
        const audioBlob = new Blob(audioChunks.current, { type: "audio/mp3" });
        onAudioRecorded(audioBlob);
        audioChunks.current = []; // Limpiar buffer
        // mediaRecorder.current.stop();
        setIsRecording(false);
      };

      mediaRecorder.current.start();
      setIsRecording(true);
    } catch (error) {
      console.error("Error al acceder al micrófono:", error);
    }
  };

  // Detener la grabación cuando el usuario suelta el botón
  const stopRecording = () => {
    if (mediaRecorder.current ) {
      console.log(mediaRecorder.current.state);
      console.log('Deteniendo grabación...');
      mediaRecorder.current.stop();
    }
  };

  return (
      <div className="recorder">
        <button ref={ mediaRecorder } 
          className='mic'
          onMouseDown={startRecording}
          onMouseUp={stopRecording}
          onTouchStart={startRecording}
          onTouchEnd={stopRecording}
        >
          {/* <img src={ micImage } alt="Grabar una pregunta" /> */}
        </button>
        <br />
        <span>
          {isRecording ? "Grabando..." : "Mantén presionado para grabar"}
        </span>
      </div>
    );
}

export default Recorder


// className={`px-4 py-2 rounded-full ${
//   recording ? "bg-red-500" : "bg-blue-500"
// } text-white`}