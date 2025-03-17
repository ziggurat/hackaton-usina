import usinaLogo from './assets/logoUsina.jpg'
import './App.css'
import Recorder from './components/Recorder'
import Response from './components/Response'
import exampleResponse from './mock-data/response.json'
import { useState } from 'react'

function App() {
   const [response, setResponse] = useState(null);

  const handleAudioRecorded = async (blob) => {
    setResponse(null);
    console.log('Audio grabado:', blob);
    // TODO: llamar a la API del router chatbot
    const formData = new FormData();
    formData.append('file', blob);

    try {
      // const response = await fetch('https://hackaton-usina-002a8d39a56a.herokuapp.com/dummy-response/');
      // const data = await response.json();
      // console.log('[API Dummy] Data de ka respuesta:', data);


      const response = await fetch('https://hackaton-usina.onrender.com/uploadaudio', {
        method: 'POST',
        body: formData,
      });
      
      console.log('RESPUESTA de la API:', response);
      const data = await response.json();
      setResponse(data);
    } catch (error) {
      console.error('ERROR al llamar a la API:', error);
      // TMP: Seteo respuesta de prueba;
      setResponse(exampleResponse);
      // return null;  
    }
  }

  const handleRecording = () => {
    setResponse(null);
  }

  const showKeyboard = () => {
    console.log('Mostrando teclado...');
  }

  return (
    <>
      <div className="header">
        <img className='logo' 
          src={usinaLogo} alt="Usina Logo" />
      </div>
      <div className="chat-container">
        <h1>En que te puedo ayudar?</h1>
        <div className='chat'>
          <div className='buttons'>
            <Recorder onAudioRecorded={handleAudioRecorded} 
              onRecord={handleRecording}/>
            
            <button className='keyboard' onClick={() => showKeyboard()}>
              {/* <img src={ keyboardImage } alt="opcion teclado" /> */}
              <span>Teclado en pantalla</span>
            </button>
          </div>
          
          {response && (
            <Response response={response} />
          )}
          
        </div>
      </div>
      <p className="read-the-docs">
        Acá puede ir un link a ayuda.
      </p>
    </>
  )
}

export default App
