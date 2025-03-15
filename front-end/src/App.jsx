import usinaLogo from './assets/logoUsina.jpg'
import './App.css'
import Recorder from './components/Recorder'
import Response from './components/Response'
import exampleResponse from './mock-data/response.json'

function App() {
  // const [response, setResponse] = useState(null);

  const handleAudioRecorded = async (blob) => {
    console.log('Audio grabado:', blob);
    // TODO: llamar a la API del router chatbot
    const formData = new FormData();
    formData.append('file', blob);

    try {
      const response = await fetch('https://hackaton-usina-002a8d39a56a.herokuapp.com/uploadaudio/', {
        method: 'POST',
        headers: new Headers({'content-type': 'application/json'}),
        body: formData
      });
      console.log('Respuesta de la API:', response);
    } catch (error) {
      console.error('Error al llamar a la API:', error);
      // return null;  
    }

    // Obtener respuesta de prueba
    try {
      // Usar respuesta de prueba
      console.log('Respuesta de PRUEBA:', exampleResponse);
    }
    catch (error) {
      console.error('Error al leer la respuesta de PRUEBA:', error);
    }
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
      <div className="chat">
        <h1>En que te puedo ayudar?</h1>
        <div className='buttons'>
          <Recorder onAudioRecorded={handleAudioRecorded}/>
          <Response response={exampleResponse} />

          {/* <button className='mic' 
            onClick={() => record()}>
            <img src={ micImage } alt="Grabar una pregunta" />
          </button> */}
          <button className='keyboard' onClick={() => showKeyboard()}>
            {/* <img src={ keyboardImage } alt="opcion teclado" /> */}
            <span>Teclado en pantalla</span>
          </button>
        </div>
      </div>
      <p className="read-the-docs">
        Acá puede ir un link a ayuda.
      </p>
    </>
  )
}

export default App
