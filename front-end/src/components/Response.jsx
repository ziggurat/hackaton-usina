import React from "react";

const Response = ({ response }) => {
  if (!response) return null; // Evita errores si no hay datos

  const { agent, text_response, question } = response;

  // Validar si el agente es uno de los valores permitidos
  const agentesValidos = ["historia", "organigrama", "tramites"];

  let utterance = new SpeechSynthesisUtterance(text_response);
  utterance.lang = 'es-AR';
  speechSynthesis.speak(utterance);

  return (
    <div style={{ border: "1px solid #ccc", padding: "10px", borderRadius: "5px", margin: "10px 0" }}>
      <p>Tu pregunta: </p><p style={{ fontSize: "16px", color: "#555", textWrap: "pretty"  }}>{question}</p>
      <h3 style={{ color: "#333", textTransform: "capitalize"}}>{agent ? agent : "Ningun agente pudo contestar su pregunta"}</h3>      
      <p style={{ fontSize: "16px", color: "#555", textWrap: "pretty"  }}>{text_response}</p>            
    </div>
  );
};

export default Response;
