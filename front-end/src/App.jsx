import usinaLogo from './assets/logo-usina.png'
import micImage from './assets/mic.svg'
import './App.css'

function App() {

  const record = () => {
    console.log('Grabando...');
  }

  const showKeyboard = () => {
    console.log('Mostrando teclado...');
  }

  return (
    <>
      <div className="header">
        <img className='logo' 
          src={usinaLogo} alt="Usina Logo" />
        <h1>En que te puedo ayudar?</h1>
      </div>
      <div className="buttons">
        <button className='mic' 
          onClick={() => record()}>
          <img src={ micImage } alt="Grabar una pregunta" />
        </button>
        <button onClick={() => showKeyboard()}>
          Teclado en pantalla
        </button>
      </div>
      <p className="read-the-docs">
        Acá puede ir un link a ayuda.
      </p>
    </>
  )
}

export default App
