import React from "react";

const Respuesta = ({ response }) => {
  if (!response) return null; // Evita errores si no hay datos

  const { agent, text_response, audio_response } = response;

  // Validar si el agente es uno de los valores permitidos
  const agentesValidos = ["historia", "organigrama", "tramites"];
  if (!agentesValidos.includes(agent)) {
    return <p>Agente no válido</p>;
  }

  return (
    <div style={{ border: "1px solid #ccc", padding: "10px", borderRadius: "5px", margin: "10px 0" }}>
      <h3 style={{ color: "#333", textTransform: "capitalize" }}>{agent}</h3>
      <p style={{ fontSize: "16px", color: "#555" }}>{text_response}</p>
      
      {audio_response && (
        <audio controls>
          <source src={audio_response} type="audio/mp3" />
          Tu navegador no soporta el elemento de audio.
        </audio>
      )}
    </div>
  );
};

export default Respuesta;
