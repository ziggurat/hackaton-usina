import { useState, useRef } from "react";
import useLongPress from '../hooks/useLongPress'
import "./Recorder.css";

const Recorder = ({ onAudioRecorded, onRecord }) =>{
  const [isRecording, setIsRecording] = useState(false);
  const mediaRecorder = useRef(null);
  const audioChunks = useRef([]);

  const onLongPress = () => {
    console.log('longpress is triggered');
    setIsRecording(true);
    startRecording();
  };

  const onPressEnd = () => {
    console.log('pressend is triggered');
    setIsRecording(false);
    stopRecording();
  };

  const defaultOptions = {
      shouldPreventDefault: true,
      delay: 500,
  };
  
  const longPressEvent = useLongPress(onLongPress, onPressEnd, defaultOptions);

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

  const stopRecording = () => {
    if (mediaRecorder.current ) {
      console.log(mediaRecorder.current.state);
      console.log('Deteniendo grabación...');
      mediaRecorder.current.stop();
    }
  };

  return (
      <div className="recorder">
        <button className={`mic ${isRecording? 'recording': ''}`}
          {...longPressEvent}>
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