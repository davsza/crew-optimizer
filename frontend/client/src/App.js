import React, {useState, useEffect} from 'react'

function App() {

  const [data, setData] = useState([{}])

  useEffect(() => {
    fetch("sample").then(
      res => res.json()
    ).then(
      data => {
        setData(data)
      }
    )
  }, [])

  return (
    <div>

      {(typeof data.sample === 'undefined') ? (
        <p>Loading...</p>
      ) : (
        data.sample.map((sample, i) => (
          <p key={i}>{sample}</p>
        ))
      )}

    </div>
  )
}

export default App
