import React from "react";

const Response = ({ response }) => {
  if (!response) return null; // Evita errores si no hay datos

  const { agent, text_response, audio_response_url } = response;

  // Validar si el agente es uno de los valores permitidos
  const agentesValidos = ["historia", "organigrama", "tramites"];

  return (
    <div style={{ border: "1px solid #ccc", padding: "10px", borderRadius: "5px", margin: "10px 0" }}>
      <h3 style={{ color: "#333", textTransform: "capitalize" }}>{agent ? agent : "(agente no definido)"}</h3>
      <p style={{ fontSize: "16px", color: "#555" }}>{text_response}</p>
      
      {audio_response_url && (
        <audio controls>
          <source src={audio_response_url} type="audio/mp3" />
          Tu navegador no soporta el elemento de audio.
        </audio>
      )}
    </div>
  );
};

export default Response;
