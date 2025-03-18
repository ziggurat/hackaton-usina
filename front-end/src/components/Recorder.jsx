import { useState, useRef, useEffect } from "react";
import { useLongPress, LongPressEventType } from 'use-long-press';
import useMediaRecorder from '../hooks/useMediaRecorder';
import "./Recorder.css";

const Recorder = ({ onAudioRecorded: notifyAudioRecorded }) =>{
  const [isRecording, setIsRecording] = useState(false);
  const { startRecording, stopRecording } = useMediaRecorder(notifyAudioRecorded);

  const recordButtonPressedCallback = async () => {
    setIsRecording(true);
    startRecording(notifyAudioRecorded);
  };

  const handlers = useLongPress(recordButtonPressedCallback, {
    onStart: (event, meta) => {
      console.log("Press started", meta);
    },
    onFinish: (event, meta) => {
      console.log("Long press finished", meta);
      setIsRecording(false);
      stopRecording();
    },
    onCancel: (event, meta) => {
      console.log("Press cancelled", meta);
      setIsRecording(false);
      stopRecording();
    },
    //onMove: () => console.log("Detected mouse or touch movement"),
    filterEvents: (event) => true, // All events can potentially trigger long press
    threshold: 100,
    captureEvent: true,
    cancelOnMovement: false,
    cancelOutsideElement: false,
    detect: LongPressEventType.Touch,
  });

  return (
      <div className="recorder">
        <button className={`mic ${isRecording? 'recording': ''}`}
          {...handlers()}
          onContextMenu={(e) => e.preventDefault()}>
        </button>
        <br />
        <span className="read-the-docs">
          {isRecording ? "Grabando..." : "Mantén presionado para grabar"}
        </span>
      </div>
    );
}

export default Recorder


// className={`px-4 py-2 rounded-full ${
//   recording ? "bg-red-500" : "bg-blue-500"
// } text-white`}