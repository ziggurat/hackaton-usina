import usinaLogo from './assets/logo-usina.png'
import keyboardImage from './assets/teclado.svg'
import './App.css'
import Recorder from './components/Recorder'

function App() {

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
          <Recorder/>
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
