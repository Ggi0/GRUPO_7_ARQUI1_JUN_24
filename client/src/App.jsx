import { useState, useEffect } from 'react'
import axios from 'axios'

function App() {

  const [selectedArea, setSelectedArea] = useState('');

  const handleAreaChange = (event) => {
    setSelectedArea(event.target.value);
    console.log('Selected index:', event.target.value);
  };

  //asdf
  // * Iluminación encendida
  const sendDataToServer = async () => {
    try {
      await axios.post('http://127.0.0.1:8000/api/onLED', {
        index: selectedArea
      });
      console.log('Datos enviados correctamente. ' + selectedArea);
    } catch (error) {
      console.error('Error al enviar los datos:', error);
    }
  };

  // * Iluminación apagada
  const sendDataToServer_1 = async () => {
    try {
      await axios.post('http://127.0.0.1:8000/api/offLED', {
        area: selectedArea
      });
      console.log('Datos enviados correctamente.');
    } catch (error) {
      console.error('Error al enviar los datos:', error);
    }
  };


  // * codigo de la recepcion
  const [clientes, setClientes] = useState(0);

  useEffect(() => {
    // Función para obtener datos del servidor
    const fetchClientes = async () => {
      try {
        const response = await axios.get('http://127.0.0.1:8000/api/contador_personas');
        setClientes(response.data.contador_personas); // Ajusta según la estructura de tu respuesta
        console.log('Estado enviado correctamente.');
      } catch (error) {
        console.error('Error al obtener los datos', error);
      }
    };

    fetchClientes();
  }, []);

  // * Codigo de la cinta transportadora
  const [bandaTransportadora, setBandaTransportadora] = useState(false);
  const [statusBanda, setStatusBanda] = useState('detenida'); // Initial state for the status of the conveyor belt 

  const handleCheckboxChange = (event) => {
    const isChecked = event.target.checked;
    setBandaTransportadora(isChecked);
    const nuevoStatusBanda = isChecked ? 'en movimiento' : 'detenida';
    setStatusBanda(nuevoStatusBanda);
    // Envía el estado al servidor Flask
    enviarEstadoAlServidor(isChecked);
  };

  const enviarEstadoAlServidor = async (isChecked) => {
    try {
      await axios.post('http://127.0.0.1:8000/api/activarMotor', {
        estado: isChecked ? 1 : 0
      });
      console.log('Estado enviado correctamente.');

    } catch (error) {
      console.error('Error al enviar el estado:', error);
    }
  };

  // * Codigo del porton automatico
  const [portonAutomatico, setPortonAutomatico] = useState(false);
  const [statusPorton, setStatusPorton] = useState('cerrado'); // Estado inicial del portón [abierto, cerrado]   

  const handleCheckboxChangeServo = (event) => {
    const isChecked = event.target.checked;
    setPortonAutomatico(isChecked);

    // Envía el estado al servidor Flask
    enviarEstadoAlServidorServo(isChecked);

    if (isChecked) {
      setStatusPorton('Abriendo Porton'); // Cambia el estado del portón a abierto 
      setTimeout(() => {
        setStatusPorton('Abierto');
      }, 3000); // Ajusta el tiempo según sea necesario 
    } else {
      setStatusPorton('Cerrando Porton'); // Cambia el estado del portón a cerrado 
      setTimeout(() => {
        setStatusPorton('Cerrado');
      }, 3000); // Ajusta el tiempo según sea necesario 
    }
  }

  const enviarEstadoAlServidorServo = async (isChecked) => {
    try {
      await axios.post('http://127.0.0.1:8000/api/activarServoMotor', {
        estado: isChecked ? 1 : 0
      });
      console.log('Estado enviado correctamente.');
    }
    catch (error) {
      console.error('Error al enviar el estado:', error);
    }
  };

  // * Codigo de la alarma
  const [alarma, setAlarma] = useState(false);

  useEffect(() => {
    // Función para obtener datos del servidor
    const fetchAlarma = async () => {
      try {
        const response  = await axios.get('http://127.0.0.1:8000/api/estado_alarma');
        setAlarma(response.data.estado_alarma_exterior); // Ajusta según la estructura de tu respuesta
        console.log('Estado enviado correctamente.');
      } catch (error) {
        console.error('Error al obtener los datos', error);
      }
    };

    fetchAlarma();
  }, []);

  // Iluminacion Exterior
  const [iluminacionExterior, setIluminacionExterior] = useState(false);

  const handleCheckboxChangeIluminacion = (event) => {
    const isChecked = event.target.checked;
    setIluminacionExterior(isChecked);
    // Envía el estado al servidor Flask
    enviarEstadoAlServidorIluminacion(isChecked);
  }

  const enviarEstadoAlServidorIluminacion = async (isChecked) => {
    try {
      await axios.post('http://127.0.0.1:8000/api/activarLEDOut', {
        estado: isChecked ? 1 : 0
      });
      console.log('Estado enviado correctamente.');
    }
    catch (error) {
      console.error('Error al enviar el estado:', error);
    }
  };

  const portfolioItems = [
    { id: 1, imgSrc: "./src/assets/img/portfolio/ilumina.jpg", alt: "Ilumina", modalId: "#portfolio-modal-1" },
    { id: 2, imgSrc: "./src/assets/img/portfolio/reception.jpg", alt: "Reception", modalId: "#portfolio-modal-2" },
    { id: 3, imgSrc: "./src/assets/img/portfolio/job.png", alt: "Job", modalId: "#portfolio-modal-3" },
    { id: 4, imgSrc: "./src/assets/img/portfolio/desccarga.png", alt: "Descarga", modalId: "#portfolio-modal-4" },
    { id: 5, imgSrc: "./src/assets/img/portfolio/alarma.jpg", alt: "Alarma", modalId: "#portfolio-modal-5" }
  ];

  return (
    <>
      <nav className="navbar navbar-expand-lg fixed-top bg-secondary text-uppercase" id="mainNav">
        <div className="container"><a className="navbar-brand" href="#page-top">SMART HOME</a><button data-bs-toggle="collapse" data-bs-target="#navbarResponsive" className="navbar-toggler text-white bg-primary text-uppercase rounded" aria-controls="navbarResponsive" aria-expanded="false" aria-label="Toggle navigation"><i className="fa fa-bars"></i></button>
          <div className="collapse navbar-collapse" id="navbarResponsive">
            <ul className="navbar-nav ms-auto">
              <li className="nav-item mx-0 mx-lg-1"></li>
              <li className="nav-item mx-0 mx-lg-1"></li>
              <li className="nav-item mx-0 mx-lg-1"></li>
            </ul>
          </div>
        </div>
      </nav>

      <header className="text-center text-white bg-primary masthead" style={{ background: 'rgb(194,43,125)', '--bs-primary': '#bc187a', '--bs-primary-rgb': '188,24,122' }}>
        <div className="container">
          <img className="img-fluid d-block mx-auto mb-5" src="./src/assets/img/OIP%20(2).png" style={{ borderStyle: 'none', borderRadius: '91px' }} alt="Logo" />
          <h1>DOME HOUSE</h1>
          <hr className="star-light" />
          <h2 className="fw-light mb-0">Automated - Safety - Efficiency</h2>
        </div>
      </header>

      <section id="portfolio" className="portfolio">
        <div className="container">
          <h2 className="text-uppercase text-center text-secondary">BRANCH AREAS</h2>
          <hr className="star-dark mb-5" />
          <div className="row">
            {portfolioItems.map(item => (
              <div className="col-md-6 col-lg-4" key={item.id}>
                <a className="d-block mx-auto portfolio-item" href={item.modalId} data-bs-toggle="modal">
                  <div className="d-flex portfolio-item-caption position-absolute h-100 w-100">
                    <div className="text-center text-white my-auto portfolio-item-caption-content w-100">
                      <i className="fa fa-search-plus fa-3x"></i>
                    </div>
                  </div>
                  <img
                    className="img-fluid"
                    src={item.imgSrc}
                    alt={item.alt}
                    style={{
                      height: "257.109px",
                      marginTop: "0px",
                      marginRight: "0px",
                      marginBottom: "0px",
                      marginLeft: "50px",
                      width: "256px"
                    }}
                  />
                </a>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="text-white bg-primary mb-0" id="about">
        <div className="container">
          <h2 className="text-uppercase text-center text-white">About</h2>
          <hr className="star-light mb-5" />
          <div className="row">
            <div className="col-lg-4 ms-auto">
              <p className="lead">
                Una empresa quiere actualizar la infraestructura de una sucursal ya que<br />
                poseen problemas para monitorizar dispositivos electrónicos y quieren que<br />
                sea de una manera más accesible y con la implementación de un servidor<br />
                con raspberry pi ya que ofrece una solución económica y práctica,
              </p>
            </div>
            <div className="col-lg-4 me-auto">
              <p className="lead">
                por ello la obtención de datos y control remoto es su principal enfoque. Para ello se precisa de una página web donde se puedan controlar distintos dispositivos y<br />
                además mostrar algunos datos de la sucursal.
              </p>
            </div>
          </div>
          <div className="text-center mt-4"></div>
        </div>
      </section>

      <section id="contact">
        <div className="container">
          <h2 className="text-uppercase text-center text-secondary mb-0">Members</h2>
          <hr className="star-dark mb-5" />
          <div className="row">
            <div className="col-lg-8 mx-auto">
              <form id="contactForm" name="sentMessage">
                <div></div>
                <div>
                  <div className="mb-0 form-floating pb-2">
                    <small className="form-text text-danger help-block"></small>
                  </div>
                </div>
                <div>
                  <div className="mb-0 form-floating pb-2">
                    <p>201905884 - Santiago Julián Barrera Reyes</p>
                    <p>201019694 - Henderson Migdo Baten Hernandez</p>
                    <p>201801300 - Selim Idair Ergon Castillo</p>
                    <p>210801521 - Jemima Solmaira Chavajay Quiejú</p>
                    <p>202100229 - Giovanni Saul Concoha Cax</p>
                    <p>202201405 - Johan Moises Cardona Rosales</p>
                    <p>202204578 - Estiben Yair Lopez Leveron</p>
                  </div>
                </div>
                <div></div>
                <div id="success"></div>
                <div></div>
              </form>
            </div>
          </div>
        </div>
      </section>

      <div className="text-center text-white copyright py-4">
        <div className="container"><small>Copyright © SMARTH HOME 2024</small></div>
      </div>
      <div className="d-lg-none scroll-to-top position-fixed rounded">
        <a className="text-center d-block rounded text-white" href="#page-top"><i className="fa fa-chevron-up"></i></a>
      </div>
      <div className="modal text-center" role="dialog" tabIndex="-1" id="portfolio-modal-1">
        <div className="modal-dialog modal-lg" role="document">
          <div className="modal-content">
            <div className="modal-header">
              <button className="btn-close" type="button" aria-label="Close" data-bs-dismiss="modal"></button>
            </div>
            <div className="modal-body">
              <div className="container text-center">
                <div className="row">
                  <div className="col-lg-8 mx-auto">
                    <h2 className="text-uppercase text-secondary mb-0">iluminación</h2>
                    <hr className="star-dark mb-5" />
                    <img className="img-fluid mb-5" src="./src/assets/img/portfolio/ilumina_1.jpg" style={{ width: 'auto', height: 'auto' }} alt="iluminación" />
                    <form>
                      {['Recepción', 'Administrativa', 'Baño', 'Conferencias', 'Carga y Descarga', 'Jardin', 'Cafetería', 'Trabajo'].map((area, index) => (
                        <div className="form-check" style={{ paddingLeft: '100px', boxShadow: '0px 0px 4px' }} key={index}>
                          <input className="form-check-input"
                            type="radio" id={`formCheck-${9 + index}`}
                            name="flexRadioDefault"
                            value={index}
                            onChange={handleAreaChange} />
                          <label className="form-check-label" htmlFor={`formCheck-${9 + index}`}>{area}</label>
                        </div>
                      ))}

                      <div style={{ margin: '15px' }}>
                        <button className="btn btn-primary" type="button" onClick={sendDataToServer} style={{ marginRight: '4px' }}>Encender</button>
                        <button className="btn btn-danger" type="button" onClick={sendDataToServer_1} style={{ marginLeft: '4px' }}>Apagar</button>
                      </div>

                    </form>
                  </div>
                </div>
              </div>
            </div>
            <div className="modal-footer pb-5">
              <a className="btn btn-primary btn-lg mx-auto rounded-pill" role="button" data-bs-dismiss="modal">
                <i className="fa fa-close"></i>&nbsp;Close Project
              </a>
            </div>
          </div>
        </div>
      </div>

      <div className="modal text-center" role="dialog" tabIndex="-1" id="portfolio-modal-2">
        <div className="modal-dialog modal-lg" role="document">
          <div className="modal-content">
            <div className="modal-header">
              <button className="btn-close" type="button" aria-label="Close" data-bs-dismiss="modal"></button>
            </div>
            <div className="modal-body">
              <div className="container text-center">
                <div className="row">
                  <div className="col-lg-8 mx-auto">
                    <h2 className="text-uppercase text-secondary mb-0"><strong>RECEPCIÓN</strong></h2>
                    <hr className="star-dark mb-5" />
                    <img className="img-fluid mb-5" src="./src/assets/img/portfolio/recepcion.png" style={{ width: 'auto', height: 'auto' }} alt="Recepción" />
                    <label className="form-label" style={{ fontSize: '20px', textShadow: '0px 0px' }}>Cantidad de Clientes en la Sucursal:&nbsp;</label>
                    <span style={{ fontSize: '20px' }}>{clientes}</span>
                  </div>
                </div>
              </div>
            </div>
            <div className="modal-footer pb-5">
              <a className="btn btn-primary btn-lg mx-auto rounded-pill" role="button" data-bs-dismiss="modal">
                <i className="fa fa-close"></i>&nbsp;Close Project
              </a>
            </div>
          </div>
        </div>
      </div>

      <div className="modal text-center" role="dialog" tabIndex="-1" id="portfolio-modal-3">
        <div className="modal-dialog modal-lg" role="document">
          <div className="modal-content">
            <div className="modal-header">
              <button className="btn-close" type="button" aria-label="Close" data-bs-dismiss="modal"></button>
            </div>
            <div className="modal-body">
              <div className="container text-center">
                <div className="row">
                  <div className="col-lg-8 mx-auto">
                    <h2 className="text-uppercase text-secondary mb-0">Área de trabajo</h2>
                    <hr className="star-dark mb-5" />
                    <img className="img-fluid mb-5" src="./src/assets/img/portfolio/cinta_1.png" />
                    <form>
                      <div className="form-check form-switch">
                        <input className="form-check-input"
                          type="checkbox" id="formCheck-1"
                          style={{ width: '42px', height: '26px' }}
                          checked={bandaTransportadora}
                          onChange={handleCheckboxChange} />
                        <label className="form-check-label"
                          htmlFor="formCheck-1"
                          style={{ boxShadow: '0px 0px 4px', fontSize: '20px', paddingRight: '10px', paddingLeft: '10px' }}>Banda transportadora</label>
                      </div>
                      <label className="form-label" style={{ fontSize: '20px', textShadow: '0px 0px' }}>Estado:&nbsp;</label>
                      <span style={{ fontSize: '20px' }}>{statusBanda}</span>
                    </form>
                  </div>
                </div>
              </div>
            </div>
            <div className="modal-footer pb-5">
              <a className="btn btn-primary btn-lg mx-auto rounded-pill" role="button" data-bs-dismiss="modal">
                <i className="fa fa-close"></i>&nbsp;Close Project
              </a>
            </div>
          </div>
        </div>
      </div>

      <div className="modal text-center" role="dialog" tabIndex="-1" id="portfolio-modal-4">
        <div className="modal-dialog modal-lg" role="document">
          <div className="modal-content">
            <div className="modal-header">
              <button className="btn-close" type="button" aria-label="Close" data-bs-dismiss="modal"></button>
            </div>
            <div className="modal-body">
              <div className="container text-center">
                <div className="row">
                  <div className="col-lg-8 mx-auto">
                    <h2 className="text-uppercase text-secondary mb-0">área de carga y descarga porton</h2>
                    <hr className="star-dark mb-5" />
                    <img className="img-fluid mb-5" src="./src/assets/img/portfolio/porton.png" />
                    <form>
                      <div className="form-check form-switch">
                        <input className="form-check-input"
                          type="checkbox" id="formCheck-2"
                          style={{ width: '42px', height: '26px' }}
                          checked={portonAutomatico}
                          onChange={handleCheckboxChangeServo} />
                        <label className="form-check-label" htmlFor="formCheck-2" style={{ boxShadow: '0px 0px 4px', fontSize: '20px', paddingRight: '10px', paddingLeft: '10px' }}>Porton</label>
                      </div>
                      <label className="form-label" style={{ fontSize: '20px', textShadow: '0px 0px' }}>Estado:&nbsp;</label>
                      <span style={{ fontSize: '20px' }}>{statusPorton}</span>
                    </form>
                  </div>
                </div>
              </div>
            </div>
            <div className="modal-footer pb-5">
              <a className="btn btn-primary btn-lg mx-auto rounded-pill" role="button" data-bs-dismiss="modal">
                <i className="fa fa-close"></i>&nbsp;Close Project
              </a>
            </div>
          </div>
        </div>
      </div>

      <div className="modal text-center" role="dialog" tabIndex="-1" id="portfolio-modal-5">
        <div className="modal-dialog modal-lg" role="document">
          <div className="modal-content">
            <div className="modal-header">
              <button className="btn-close" type="button" aria-label="Close" data-bs-dismiss="modal"></button>
            </div>
            <div className="modal-body">
              <div className="container text-center">
                <div className="row">
                  <div className="col-lg-8 mx-auto">
                    <h2 className="text-uppercase text-secondary mb-0">Area perimetral</h2>
                    <hr className="star-dark mb-5" />
                    <img className="img-fluid mb-5" src="./src/assets/img/portfolio/exterior.jpg" />
                    <div className="form-check form-switch">
                      <input className="form-check-input"
                        type="checkbox" id="formCheck-1"
                        style={{ width: '42px', height: '26px' }}
                        checked={iluminacionExterior}
                        onChange={handleCheckboxChangeIluminacion} />
                      <label className="form-check-label"
                        htmlFor="formCheck-1"
                        style={{ boxShadow: '0px 0px 4px', fontSize: '20px', paddingRight: '10px', paddingLeft: '10px' }}>Iluminación Exterior</label>
                    </div>
                    <br></br>
                    <label className="form-label" style={{ fontSize: '20px', textShadow: '0px 0px' }}>Estado de la Alarma:&nbsp;</label>
                    <span style={{ fontSize: '20px' }}>{alarma}</span>
                  </div>
                </div>
              </div>
            </div>
            <div className="modal-footer pb-5">
              <a className="btn btn-primary btn-lg mx-auto rounded-pill" role="button" data-bs-dismiss="modal">
                <i className="fa fa-close"></i>&nbsp;Close Project
              </a>
            </div>
          </div>
        </div>
      </div>

    </>
  )
}

export default App
