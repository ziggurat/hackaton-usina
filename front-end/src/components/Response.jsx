import React from "react";

const Response = ({ response }) => {
  if (!response) return null; // Evita errores si no hay datos

  const { agent, text_response, audio_response_url } = response;

  // Validar si el agente es uno de los valores permitidos
  const agentesValidos = ["historia", "organigrama", "tramites"];

  let utterance = new SpeechSynthesisUtterance(text_response);
  speechSynthesis.speak(utterance);

  return (
    <div style={{ border: "1px solid #ccc", padding: "10px", borderRadius: "5px", margin: "10px 0" }}>
      <h3 style={{ color: "#333", textTransform: "capitalize"}}>{agent ? agent : "Ningun agente pudo contestar su pregunta"}</h3>
      <p style={{ fontSize: "16px", color: "#555", textWrap: "pretty"  }}>{text_response}</p>
      
      {audio_response_url}
    </div>
  );
};

export default Response;
