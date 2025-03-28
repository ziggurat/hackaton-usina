import { useRef } from 'react';

function useMediaRecorder() {
  const mediaRecorder = useRef(null);
  const audioChunks = useRef([]);

  const startRecording = async (notifyAudioRecorded) => {
    try {
      console.log("Iniciando grabación...");
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorder.current = new MediaRecorder(stream);

      mediaRecorder.current.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunks.current.push(event.data);
        }
      };

      mediaRecorder.current.onstop = () => {
        console.log("Grabación finalizada");
        const audioBlob = new Blob(audioChunks.current, { type: "audio/mp3" });
        notifyAudioRecorded(audioBlob);
        audioChunks.current = []; // Limpiar buffer
      };

      mediaRecorder.current.start();
    } catch (error) {
      console.error("Error al acceder al micrófono:", error);
    }
  };

  const stopRecording = () => {
    if (mediaRecorder.current && mediaRecorder.current.state === 'recording') {
      mediaRecorder.current.stop();
    }
  };

  return { startRecording, stopRecording };
}

export default useMediaRecorder;

// const mediaRecorder = useRef(null);
// const audioChunks = useRef([]);

// // Iniciar la grabación cuando el usuario presiona el botón
// export const startRecording = async () => {
//     try {
//       onRecord();
//       const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
//       mediaRecorder.current = new MediaRecorder(stream);

//       mediaRecorder.current.ondataavailable = (event) => {
//         if (event.data.size > 0) {
//           audioChunks.current.push(event.data);
//         }
//       };

//       mediaRecorder.current.onstop = () => {
//         const audioBlob = new Blob(audioChunks.current, { type: "audio/mp3" });
//         onAudioRecorded(audioBlob);
//         audioChunks.current = []; // Limpiar buffer
//       };

//       mediaRecorder.current.start();
//     } catch (error) {
//       console.error("Error al acceder al micrófono:", error);
//     }
//   };

// export const stopRecording = () => {
//   if (mediaRecorder.current && mediaRecorder.current.state === 'recording') {
//     mediaRecorder.current.stop();
//   }
// };