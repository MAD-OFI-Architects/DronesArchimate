# Matriz de trazabilidad modelo → código

**Conformidad: 109/109 = 100.0%** (símbolos obligatorios declarados en su capa).

| Dominio | Capa | Tipo | Símbolo | Elemento del modelo | Archivo | Estado |
|---|---|---|---|---|---|---|
| Intervenciones | domain | aggregate_root | `OrdenDeTrabajo` | id-80f31c8bbef151fd8e9769d632d4c453 | services/intervenciones/src/Intervenciones.Domain/OrdenDeTrabajo.cs | ✅ |
| Intervenciones | domain | memento | `OrdenDeTrabajoMemento` | id-80f31c8bbef151fd8e9769d632d4c453 | services/intervenciones/src/Intervenciones.Domain/OrdenDeTrabajoMemento.cs | ✅ |
| Intervenciones | domain | repository_port | `IOrdenDeTrabajoRepository` | id-80f31c8bbef151fd8e9769d632d4c453 | services/intervenciones/src/Intervenciones.Domain/IOrdenDeTrabajoRepository.cs | ✅ |
| Intervenciones | domain | entity | `TareaEjecutada` | id-2614ed50b81f581e9e80eba5c6d4f747 | services/intervenciones/src/Intervenciones.Domain/TareaEjecutada.cs | ✅ |
| Intervenciones | domain | entity | `ConsumoDeRepuesto` | id-a43cf8daf2af50aabe60fad221797f77 | services/intervenciones/src/Intervenciones.Domain/ConsumoDeRepuesto.cs | ✅ |
| Intervenciones | domain | entity | `Liberacion` | id-22fbab25ef985b43a7b04e3e2844cb4a | services/intervenciones/src/Intervenciones.Domain/Liberacion.cs | ✅ |
| Intervenciones | domain | value_object | `TipoDeOrden` | id-eb2b07676b125137bb421364f66d90f9 | services/intervenciones/src/Intervenciones.Domain/TipoDeOrden.cs | ✅ |
| Intervenciones | domain | value_object | `EstadoDeLaOrden` | id-ef919e2ba876545296d759560bbd49a1 | services/intervenciones/src/Intervenciones.Domain/Estados/EstadoDeLaOrden.cs | ✅ |
| Intervenciones | domain | value_object | `Hallazgo` | id-4409ab349ad350af870d384fad153648 | services/intervenciones/src/Intervenciones.Domain/Hallazgo.cs | ✅ |
| Intervenciones | domain | value_object | `HorasHombre` | id-ca84f092696253989edc05661a743097 | services/intervenciones/src/Intervenciones.Domain/HorasHombre.cs | ✅ |
| Intervenciones | domain | value_object | `HoraDeCorte` | id-c387cf827925568c82bf04d2e5306ccd | services/intervenciones/src/Intervenciones.Domain/HoraDeCorte.cs | ✅ |
| Intervenciones | domain | value_object | `VueloDePrueba` | id-05bb42dc7fe75c2fb09a8136cf9babc2 | services/intervenciones/src/Intervenciones.Domain/VueloDePrueba.cs | ✅ |
| Intervenciones | infrastructure | repository | `RepositorioOrdenDeTrabajo` | id-80f31c8bbef151fd8e9769d632d4c453 | services/intervenciones/src/Intervenciones.Infrastructure/Persistencia/RepositorioOrdenDeTrabajo.cs | ✅ |
| Intervenciones | infrastructure | cache_decorator | `RepositorioCacheadoOrdenDeTrabajo` | id-80f31c8bbef151fd8e9769d632d4c453 | services/intervenciones/src/Intervenciones.Infrastructure/Persistencia/RepositorioCacheadoOrdenDeTrabajo.cs | ✅ |
| Intervenciones | application | dto | `OrdenDeTrabajoDto` | id-80f31c8bbef151fd8e9769d632d4c453 | services/intervenciones/src/Intervenciones.Application/Consultas/OrdenDeTrabajoDto.cs | ✅ |
| Intervenciones | application | mapper | `OrdenDeTrabajoMapeador` | id-80f31c8bbef151fd8e9769d632d4c453 | services/intervenciones/src/Intervenciones.Application/Consultas/OrdenDeTrabajoMapeador.cs | ✅ |
| Intervenciones | application | query | `ObtenerOrdenDeTrabajoConsulta` | id-80f31c8bbef151fd8e9769d632d4c453 | services/intervenciones/src/Intervenciones.Application/Consultas/ObtenerOrdenDeTrabajoConsulta.cs | ✅ |
| Intervenciones | application | query_handler | `ObtenerOrdenDeTrabajoManejador` | id-80f31c8bbef151fd8e9769d632d4c453 | services/intervenciones/src/Intervenciones.Application/Consultas/ObtenerOrdenDeTrabajoManejador.cs | ✅ |
| Intervenciones | domain | domain_event | `OrdenDeTrabajoAbierta` | id-37c65e407a6158e8b18cc26bc7850101 | services/intervenciones/src/Intervenciones.Domain/Eventos/OrdenDeTrabajoAbierta.cs | ✅ |
| Intervenciones | domain | domain_event | `TecnicoAsignado` | id-ed6d0bf3c052579a94ea998a3a79a3d8 | services/intervenciones/src/Intervenciones.Domain/Eventos/TecnicoAsignado.cs | ✅ |
| Intervenciones | domain | domain_event | `EjecucionDeTareaRegistrada` | id-636018f8a4e459e59d3dbaa5c93cf31c | services/intervenciones/src/Intervenciones.Domain/Eventos/EjecucionDeTareaRegistrada.cs | ✅ |
| Intervenciones | domain | domain_event | `ConsumoDeRepuestoRegistrado` | id-9ede4d576530548f893b9c5f53a96e63 | services/intervenciones/src/Intervenciones.Domain/Eventos/ConsumoDeRepuestoRegistrado.cs | ✅ |
| Intervenciones | domain | domain_event | `HallazgoRegistrado` | id-12abc98c87d258cb8317cb5cd752dc5b | services/intervenciones/src/Intervenciones.Domain/Eventos/HallazgoRegistrado.cs | ✅ |
| Intervenciones | domain | domain_event | `VueloDePruebaRegistrado` | id-a71f352ec9ec59d79c6d430616a04fe9 | services/intervenciones/src/Intervenciones.Domain/Eventos/VueloDePruebaRegistrado.cs | ✅ |
| Intervenciones | domain | domain_event | `DronLiberado` | id-fa547a50f0a45970bc2f2d1d037ffe97 | services/intervenciones/src/Intervenciones.Domain/Eventos/DronLiberado.cs | ✅ |
| Intervenciones | domain | domain_event | `OrdenDeTrabajoCerrada` | id-91d95677233e5eca8491c72a0c266c55 | services/intervenciones/src/Intervenciones.Domain/Eventos/OrdenDeTrabajoCerrada.cs | ✅ |
| Intervenciones | domain | domain_event | `OrdenDeTrabajoPuestaEnEspera` | id-ade99776d77853e4ad64a9e67adfda53 | services/intervenciones/src/Intervenciones.Domain/Eventos/OrdenDeTrabajoPuestaEnEspera.cs | ✅ |
| Intervenciones | domain | business_rule | `OrdenCerradaInmutable` | ORDEN_CERRADA_INMUTABLE | services/intervenciones/src/Intervenciones.Domain/Reglas/OrdenCerradaInmutable.cs | ✅ |
| Intervenciones | domain | business_rule | `ParadaInexistente` | PARADA_INEXISTENTE | services/intervenciones/src/Intervenciones.Domain/Reglas/ParadaInexistente.cs | ✅ |
| Intervenciones | domain | business_rule | `SerieFaltante` | SERIE_FALTANTE | services/intervenciones/src/Intervenciones.Domain/Reglas/SerieFaltante.cs | ✅ |
| Intervenciones | domain | business_rule | `LiberaElMismoQueEjecuto` | LIBERA_EL_MISMO_QUE_EJECUTO | services/intervenciones/src/Intervenciones.Domain/Reglas/LiberaElMismoQueEjecuto.cs | ✅ |
| Intervenciones | application | command | `AbrirOrdenDeTrabajoComando` | id-26a08bfcad335feca3ecb1f2a104c4ab | services/intervenciones/src/Intervenciones.Application/Comandos/AbrirOrdenDeTrabajoComando.cs | ✅ |
| Intervenciones | application | command_handler | `AbrirOrdenDeTrabajoManejador` | id-26a08bfcad335feca3ecb1f2a104c4ab | services/intervenciones/src/Intervenciones.Application/Comandos/AbrirOrdenDeTrabajoManejador.cs | ✅ |
| Intervenciones | application | validator | `AbrirOrdenDeTrabajoValidador` | id-26a08bfcad335feca3ecb1f2a104c4ab | services/intervenciones/src/Intervenciones.Application/Comandos/AbrirOrdenDeTrabajoValidador.cs | ✅ |
| Intervenciones | api | request_model | `AbrirOrdenDeTrabajoSolicitud` | id-26a08bfcad335feca3ecb1f2a104c4ab | services/intervenciones/src/Intervenciones.Api/Solicitudes/AbrirOrdenDeTrabajoSolicitud.cs | ✅ |
| Intervenciones | tests | test | `AbrirOrdenDeTrabajoComando` | id-26a08bfcad335feca3ecb1f2a104c4ab | services/intervenciones/tests/Intervenciones.Tests/Soporte/EscenarioDeIntervenciones.cs | ✅ |
| Intervenciones | application | command | `AsignarTecnicoComando` | id-17d39de3eafd5e35b755dcf7c7cad0c5 | services/intervenciones/src/Intervenciones.Application/Comandos/AsignarTecnicoComando.cs | ✅ |
| Intervenciones | application | command_handler | `AsignarTecnicoManejador` | id-17d39de3eafd5e35b755dcf7c7cad0c5 | services/intervenciones/src/Intervenciones.Application/Comandos/AsignarTecnicoManejador.cs | ✅ |
| Intervenciones | application | validator | `AsignarTecnicoValidador` | id-17d39de3eafd5e35b755dcf7c7cad0c5 | services/intervenciones/src/Intervenciones.Application/Comandos/AsignarTecnicoValidador.cs | ✅ |
| Intervenciones | api | request_model | `AsignarTecnicoSolicitud` | id-17d39de3eafd5e35b755dcf7c7cad0c5 | services/intervenciones/src/Intervenciones.Api/Solicitudes/AsignarTecnicoSolicitud.cs | ✅ |
| Intervenciones | tests | test | `AsignarTecnicoComando` | id-17d39de3eafd5e35b755dcf7c7cad0c5 | services/intervenciones/tests/Intervenciones.Tests/Application/ComandosTests.cs | ✅ |
| Intervenciones | application | command | `RegistrarEjecucionDeTareaComando` | id-b6722407c62b553da0e9cbab6a2fdc05 | services/intervenciones/src/Intervenciones.Application/Comandos/RegistrarEjecucionDeTareaComando.cs | ✅ |
| Intervenciones | application | command_handler | `RegistrarEjecucionDeTareaManejador` | id-b6722407c62b553da0e9cbab6a2fdc05 | services/intervenciones/src/Intervenciones.Application/Comandos/RegistrarEjecucionDeTareaManejador.cs | ✅ |
| Intervenciones | application | validator | `RegistrarEjecucionDeTareaValidador` | id-b6722407c62b553da0e9cbab6a2fdc05 | services/intervenciones/src/Intervenciones.Application/Comandos/RegistrarEjecucionDeTareaValidador.cs | ✅ |
| Intervenciones | api | request_model | `RegistrarEjecucionDeTareaSolicitud` | id-b6722407c62b553da0e9cbab6a2fdc05 | services/intervenciones/src/Intervenciones.Api/Solicitudes/RegistrarEjecucionDeTareaSolicitud.cs | ✅ |
| Intervenciones | tests | test | `RegistrarEjecucionDeTareaComando` | id-b6722407c62b553da0e9cbab6a2fdc05 | services/intervenciones/tests/Intervenciones.Tests/Application/ConsumidoresTests.cs | ✅ |
| Intervenciones | application | command | `RegistrarConsumoDeRepuestoComando` | id-1755cead67e45528ae39c1234d8d1ab1 | services/intervenciones/src/Intervenciones.Application/Comandos/RegistrarConsumoDeRepuestoComando.cs | ✅ |
| Intervenciones | application | command_handler | `RegistrarConsumoDeRepuestoManejador` | id-1755cead67e45528ae39c1234d8d1ab1 | services/intervenciones/src/Intervenciones.Application/Comandos/RegistrarConsumoDeRepuestoManejador.cs | ✅ |
| Intervenciones | application | validator | `RegistrarConsumoDeRepuestoValidador` | id-1755cead67e45528ae39c1234d8d1ab1 | services/intervenciones/src/Intervenciones.Application/Comandos/RegistrarConsumoDeRepuestoValidador.cs | ✅ |
| Intervenciones | api | request_model | `RegistrarConsumoDeRepuestoSolicitud` | id-1755cead67e45528ae39c1234d8d1ab1 | services/intervenciones/src/Intervenciones.Api/Solicitudes/RegistrarConsumoDeRepuestoSolicitud.cs | ✅ |
| Intervenciones | tests | test | `RegistrarConsumoDeRepuestoComando` | id-1755cead67e45528ae39c1234d8d1ab1 | services/intervenciones/tests/Intervenciones.Tests/Application/ComandosTests.cs | ✅ |
| Intervenciones | application | command | `RegistrarHallazgoComando` | id-2beefb5d6d8a54c8b6552729e3c954bb | services/intervenciones/src/Intervenciones.Application/Comandos/RegistrarHallazgoComando.cs | ✅ |
| Intervenciones | application | command_handler | `RegistrarHallazgoManejador` | id-2beefb5d6d8a54c8b6552729e3c954bb | services/intervenciones/src/Intervenciones.Application/Comandos/RegistrarHallazgoManejador.cs | ✅ |
| Intervenciones | application | validator | `RegistrarHallazgoValidador` | id-2beefb5d6d8a54c8b6552729e3c954bb | services/intervenciones/src/Intervenciones.Application/Comandos/RegistrarHallazgoValidador.cs | ✅ |
| Intervenciones | api | request_model | `RegistrarHallazgoSolicitud` | id-2beefb5d6d8a54c8b6552729e3c954bb | services/intervenciones/src/Intervenciones.Api/Solicitudes/RegistrarHallazgoSolicitud.cs | ✅ |
| Intervenciones | tests | test | `RegistrarHallazgoComando` | id-2beefb5d6d8a54c8b6552729e3c954bb | services/intervenciones/tests/Intervenciones.Tests/Application/ComandosTests.cs | ✅ |
| Intervenciones | application | command | `RegistrarVueloDePruebaComando` | id-d01c5da31c7b51b5836b7dff871388de | services/intervenciones/src/Intervenciones.Application/Comandos/RegistrarVueloDePruebaComando.cs | ✅ |
| Intervenciones | application | command_handler | `RegistrarVueloDePruebaManejador` | id-d01c5da31c7b51b5836b7dff871388de | services/intervenciones/src/Intervenciones.Application/Comandos/RegistrarVueloDePruebaManejador.cs | ✅ |
| Intervenciones | application | validator | `RegistrarVueloDePruebaValidador` | id-d01c5da31c7b51b5836b7dff871388de | services/intervenciones/src/Intervenciones.Application/Comandos/RegistrarVueloDePruebaValidador.cs | ✅ |
| Intervenciones | api | request_model | `RegistrarVueloDePruebaSolicitud` | id-d01c5da31c7b51b5836b7dff871388de | services/intervenciones/src/Intervenciones.Api/Solicitudes/RegistrarVueloDePruebaSolicitud.cs | ✅ |
| Intervenciones | tests | test | `RegistrarVueloDePruebaComando` | id-d01c5da31c7b51b5836b7dff871388de | services/intervenciones/tests/Intervenciones.Tests/Application/ComandosTests.cs | ✅ |
| Intervenciones | application | command | `LiberarDronComando` | id-94bcfc9f207b57769179759ba24363e3 | services/intervenciones/src/Intervenciones.Application/Comandos/LiberarDronComando.cs | ✅ |
| Intervenciones | application | command_handler | `LiberarDronManejador` | id-94bcfc9f207b57769179759ba24363e3 | services/intervenciones/src/Intervenciones.Application/Comandos/LiberarDronManejador.cs | ✅ |
| Intervenciones | application | validator | `LiberarDronValidador` | id-94bcfc9f207b57769179759ba24363e3 | services/intervenciones/src/Intervenciones.Application/Comandos/LiberarDronValidador.cs | ✅ |
| Intervenciones | api | request_model | `LiberarDronSolicitud` | id-94bcfc9f207b57769179759ba24363e3 | services/intervenciones/src/Intervenciones.Api/Solicitudes/LiberarDronSolicitud.cs | ✅ |
| Intervenciones | tests | test | `LiberarDronComando` | id-94bcfc9f207b57769179759ba24363e3 | services/intervenciones/tests/Intervenciones.Tests/Application/ConsumidoresTests.cs | ✅ |
| Intervenciones | application | command | `CerrarOrdenDeTrabajoComando` | id-6de9e2be1ea65910b8239ae4a23a3601 | services/intervenciones/src/Intervenciones.Application/Comandos/CerrarOrdenDeTrabajoComando.cs | ✅ |
| Intervenciones | application | command_handler | `CerrarOrdenDeTrabajoManejador` | id-6de9e2be1ea65910b8239ae4a23a3601 | services/intervenciones/src/Intervenciones.Application/Comandos/CerrarOrdenDeTrabajoManejador.cs | ✅ |
| Intervenciones | application | validator | `CerrarOrdenDeTrabajoValidador` | id-6de9e2be1ea65910b8239ae4a23a3601 | services/intervenciones/src/Intervenciones.Application/Comandos/CerrarOrdenDeTrabajoValidador.cs | ✅ |
| Intervenciones | api | request_model | `CerrarOrdenDeTrabajoSolicitud` | id-6de9e2be1ea65910b8239ae4a23a3601 | services/intervenciones/src/Intervenciones.Api/Solicitudes/CerrarOrdenDeTrabajoSolicitud.cs | ✅ |
| Intervenciones | tests | test | `CerrarOrdenDeTrabajoComando` | id-6de9e2be1ea65910b8239ae4a23a3601 | services/intervenciones/tests/Intervenciones.Tests/Application/ConsumidoresTests.cs | ✅ |
| Intervenciones | application | command | `PonerOrdenEnEsperaComando` | id-2d70d5f9502b5c2bb4dfa75ef82f7b8b | services/intervenciones/src/Intervenciones.Application/Comandos/PonerOrdenEnEsperaComando.cs | ✅ |
| Intervenciones | application | command_handler | `PonerOrdenEnEsperaManejador` | id-2d70d5f9502b5c2bb4dfa75ef82f7b8b | services/intervenciones/src/Intervenciones.Application/Comandos/PonerOrdenEnEsperaManejador.cs | ✅ |
| Intervenciones | application | validator | `PonerOrdenEnEsperaValidador` | id-2d70d5f9502b5c2bb4dfa75ef82f7b8b | services/intervenciones/src/Intervenciones.Application/Comandos/PonerOrdenEnEsperaValidador.cs | ✅ |
| Intervenciones | api | request_model | `PonerOrdenEnEsperaSolicitud` | id-2d70d5f9502b5c2bb4dfa75ef82f7b8b | services/intervenciones/src/Intervenciones.Api/Solicitudes/PonerOrdenEnEsperaSolicitud.cs | ✅ |
| Intervenciones | tests | test | `PonerOrdenEnEsperaComando` | id-2d70d5f9502b5c2bb4dfa75ef82f7b8b | services/intervenciones/tests/Intervenciones.Tests/Application/ComandosTests.cs | ✅ |
| Intervenciones | contracts | published_contract | `OrdenDeTrabajoCerradaV1` | Orden de trabajo cerrada | services/intervenciones/src/Intervenciones.Contracts/OrdenDeTrabajoCerradaV1.cs | ✅ |
| Intervenciones | application | event_translator | `OrdenDeTrabajoCerradaTraductor` | Orden de trabajo cerrada | services/intervenciones/src/Intervenciones.Application/Traductores/OrdenDeTrabajoCerradaTraductor.cs | ✅ |
| Intervenciones | contracts | topics | `IntervencionesTopicos` | Intervenciones | services/intervenciones/src/Intervenciones.Contracts/IntervencionesTopicos.cs | ✅ |
| Intervenciones | application | event_consumer | `ParadaProgramadaConsumidor` | Parada programada | services/intervenciones/src/Intervenciones.Application/Consumidores/ParadaProgramadaConsumidor.cs | ✅ |
| Intervenciones | application | event_consumer | `FaltanteDetectadoConsumidor` | Faltante detectado | services/intervenciones/src/Intervenciones.Application/Consumidores/FaltanteDetectadoConsumidor.cs | ✅ |
| Intervenciones | application | acl_port | `IConsultaDeHabilitacion` | Habilitación de Personal | services/intervenciones/src/Intervenciones.Application/Puertos/IConsultaDeHabilitacion.cs | ✅ |
| Intervenciones | infrastructure | acl_adapter | `ConsultaDeHabilitacionAdapter` | Habilitación de Personal | services/intervenciones/src/Intervenciones.Infrastructure/Habilitacion/ConsultaDeHabilitacionAdapter.cs | ✅ |
| Intervenciones | application | crypto_port | `Cifrador` |  | services/intervenciones/src/Intervenciones.Application/Puertos/Cifrador.cs | ✅ |
| Intervenciones | infrastructure | crypto_impl | `CifradorAes` |  | services/intervenciones/src/Intervenciones.Infrastructure/Cifrado/CifradorAes.cs | ✅ |
| Intervenciones | infrastructure | event_publisher | `PublicadorDeEventosHttp` |  | services/intervenciones/src/Intervenciones.Infrastructure/Mensajeria/PublicadorDeEventosHttp.cs | ✅ |
| Intervenciones | api | endpoints | `IntervencionesEndpoints` | Intervenciones | services/intervenciones/src/Intervenciones.Api/IntervencionesEndpoints.cs | ✅ |
| Intervenciones | api | composition_root | `IntervencionesComposicion` | Intervenciones | services/intervenciones/src/Intervenciones.Api/IntervencionesComposicion.cs | ✅ |
| Intervenciones | infrastructure | infra_pattern | `BandejaDeSalida` |  | services/intervenciones/src/BuildingBlocks/BuildingBlocks.Infrastructure/Outbox/BandejaDeSalida.cs | ✅ |
| Intervenciones | infrastructure | infra_pattern | `ProcesadorDeMensajeEntrante` |  | services/intervenciones/src/BuildingBlocks/BuildingBlocks.Infrastructure/Mensajeria/ProcesadorDeMensajeEntrante.cs | ✅ |
| Intervenciones | ops | file | `Dockerfile` |  | services/intervenciones/Dockerfile | ✅ |
| Intervenciones | ops | file | `README.md` |  | services/intervenciones/README.md | ✅ |
| Intervenciones | ops | file | `proyecto` |  | services/intervenciones/Intervenciones.sln | ✅ |
| Intervenciones | api | route | `/api/orden-de-trabajo` | id-26a08bfcad335feca3ecb1f2a104c4ab | services/intervenciones/tests/Intervenciones.Tests/Api/OrdenDeTrabajoHttpTests.cs | ✅ |
| Intervenciones | api | route | `asignar-tecnico` | id-17d39de3eafd5e35b755dcf7c7cad0c5 | services/intervenciones/tests/Intervenciones.Tests/Api/OrdenDeTrabajoHttpTests.cs | ✅ |
| Intervenciones | api | route | `registrar-ejecucion-de-tarea` | id-b6722407c62b553da0e9cbab6a2fdc05 | services/intervenciones/tests/Intervenciones.Tests/Api/OrdenDeTrabajoHttpTests.cs | ✅ |
| Intervenciones | api | route | `registrar-consumo-de-repuesto` | id-1755cead67e45528ae39c1234d8d1ab1 | services/intervenciones/tests/Intervenciones.Tests/Api/OrdenDeTrabajoHttpTests.cs | ✅ |
| Intervenciones | api | route | `registrar-hallazgo` | id-2beefb5d6d8a54c8b6552729e3c954bb | services/intervenciones/tests/Intervenciones.Tests/Api/OrdenDeTrabajoHttpTests.cs | ✅ |
| Intervenciones | api | route | `registrar-vuelo-de-prueba` | id-d01c5da31c7b51b5836b7dff871388de | services/intervenciones/tests/Intervenciones.Tests/Api/OrdenDeTrabajoHttpTests.cs | ✅ |
| Intervenciones | api | route | `liberar-dron` | id-94bcfc9f207b57769179759ba24363e3 | services/intervenciones/tests/Intervenciones.Tests/Api/OrdenDeTrabajoHttpTests.cs | ✅ |
| Intervenciones | api | route | `cerrar-orden-de-trabajo` | id-6de9e2be1ea65910b8239ae4a23a3601 | services/intervenciones/tests/Intervenciones.Tests/Api/OrdenDeTrabajoHttpTests.cs | ✅ |
| Intervenciones | api | route | `poner-orden-en-espera` | id-2d70d5f9502b5c2bb4dfa75ef82f7b8b | services/intervenciones/tests/Intervenciones.Tests/Api/OrdenDeTrabajoHttpTests.cs | ✅ |
| Intervenciones | frontend | form | `AsignarTecnicoForm` | Asignar técnico | frontend/mfe-intervenciones/src/forms/AsignarTecnicoForm.tsx | ✅ |
| Intervenciones | frontend | form | `RegistrarEjecucionDeTareaForm` | Registrar ejecución de tarea | frontend/mfe-intervenciones/src/forms/RegistrarEjecucionDeTareaForm.tsx | ✅ |
| Intervenciones | frontend | form | `RegistrarConsumoDeRepuestoForm` | Registrar consumo de repuesto | frontend/mfe-intervenciones/src/forms/RegistrarConsumoDeRepuestoForm.tsx | ✅ |
| Intervenciones | frontend | form | `RegistrarHallazgoForm` | Registrar hallazgo | frontend/mfe-intervenciones/src/forms/RegistrarHallazgoForm.tsx | ✅ |
| Intervenciones | frontend | form | `RegistrarVueloDePruebaForm` | Registrar vuelo de prueba | frontend/mfe-intervenciones/src/forms/RegistrarVueloDePruebaForm.tsx | ✅ |
| Intervenciones | frontend | form | `LiberarDronForm` | Liberar dron | frontend/mfe-intervenciones/src/forms/LiberarDronForm.tsx | ✅ |
| Intervenciones | frontend | form | `CerrarOrdenDeTrabajoForm` | Cerrar orden de trabajo | frontend/mfe-intervenciones/src/forms/CerrarOrdenDeTrabajoForm.tsx | ✅ |
