import React, { useEffect, useState } from "react";

function App() {
  const [msg, setMsg] = useState("");

  useEffect(() => {
    fetch("/.netlify/functions/hello")
      .then(res => res.json())
      .then(data => setMsg(data.message));
  }, []);

  return (
    <div>
      <h1>Netlify Test</h1>
      <p>API'den gelen mesaj: {msg}</p>
    </div>
  );
}

export default App; 