import { useState, useRef } from "react";
import micImage from '../assets/mic.svg'
import "./Recorder.css";
import useLongPress from '../hooks/useLongPress'

const Recorder = ({ onAudioRecorded, onRecord }) =>{
  const [isRecording, setIsRecording] = useState(false);

  const onLongPress = () => {
    console.log('longpress is triggered');
    setIsRecording(true);
  };

  const onPressEnd = () => {
    console.log('pressend is triggered');
    setIsRecording(false);
  };

  const onClick = () => {
      console.log('click is triggered')
  }

  const defaultOptions = {
      shouldPreventDefault: true,
      delay: 500,
  };
  
  const longPressEvent = useLongPress(onLongPress, onClick, onPressEnd, defaultOptions);

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