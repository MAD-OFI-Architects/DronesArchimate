# Matriz de trazabilidad modelo → código

**Conformidad: 100/100 = 100.0%** (símbolos obligatorios declarados en su capa).

| Dominio | Capa | Tipo | Símbolo | Elemento del modelo | Archivo | Estado |
|---|---|---|---|---|---|---|
| Repuestos del Taller | domain | aggregate_root | `Existencia` | id-85fe8f482b795505bb6ed73668179285 | services/repuestos-del-taller/src/repuestos_del_taller/domain/existencias/existencia.py | ✅ |
| Repuestos del Taller | domain | memento | `ExistenciaMemento` | id-85fe8f482b795505bb6ed73668179285 | services/repuestos-del-taller/src/repuestos_del_taller/domain/existencias/memento.py | ✅ |
| Repuestos del Taller | domain | repository_port | `IExistenciaRepository` | id-85fe8f482b795505bb6ed73668179285 | services/repuestos-del-taller/src/repuestos_del_taller/domain/existencias/repositorio.py | ✅ |
| Repuestos del Taller | domain | entity | `ReservaDeRepuesto` | id-28c029205b7957328660b9b3e37c65f0 | services/repuestos-del-taller/src/repuestos_del_taller/domain/existencias/reserva_de_repuesto.py | ✅ |
| Repuestos del Taller | domain | value_object | `StockMinimo` | id-e73ac1e2f3925e269b40673d49eed562 | services/repuestos-del-taller/src/repuestos_del_taller/domain/existencias/existencia.py | ✅ |
| Repuestos del Taller | domain | value_object | `Cantidad` | id-b415f91f6d3153d1b0a3049caf0a7046 | services/repuestos-del-taller/src/repuestos_del_taller/domain/reposicion/solicitud_de_reposicion.py | ✅ |
| Repuestos del Taller | domain | value_object | `PlazoDeEntrega` | id-29e5404b239f5f68b56cb4606b0614f7 | services/repuestos-del-taller/src/repuestos_del_taller/domain/existencias/objetos_de_valor.py | ✅ |
| Repuestos del Taller | infrastructure | repository | `RepositorioExistencia` | id-85fe8f482b795505bb6ed73668179285 | services/repuestos-del-taller/src/repuestos_del_taller/adapters/outbound/persistencia.py | ✅ |
| Repuestos del Taller | infrastructure | cache_decorator | `RepositorioCacheadoExistencia` | id-85fe8f482b795505bb6ed73668179285 | services/repuestos-del-taller/src/repuestos_del_taller/adapters/outbound/persistencia.py | ✅ |
| Repuestos del Taller | domain | aggregate_root | `SolicitudDeReposicion` | id-766c6a84908053728dd7ac3f9a5060ae | services/repuestos-del-taller/src/repuestos_del_taller/domain/reposicion/solicitud_de_reposicion.py | ✅ |
| Repuestos del Taller | domain | memento | `SolicitudDeReposicionMemento` | id-766c6a84908053728dd7ac3f9a5060ae | services/repuestos-del-taller/src/repuestos_del_taller/domain/reposicion/memento.py | ✅ |
| Repuestos del Taller | domain | repository_port | `ISolicitudDeReposicionRepository` | id-766c6a84908053728dd7ac3f9a5060ae | services/repuestos-del-taller/src/repuestos_del_taller/domain/reposicion/repositorio.py | ✅ |
| Repuestos del Taller | domain | value_object | `CantidadSolicitada` | id-0797d8cac1ac55feaa30c88f1218100b | services/repuestos-del-taller/src/repuestos_del_taller/domain/reposicion/objetos_de_valor.py | ✅ |
| Repuestos del Taller | domain | value_object | `NivelDeAprobacion` | id-7be276b4f1685e18a3909e84ed4183b9 | services/repuestos-del-taller/src/repuestos_del_taller/domain/reposicion/objetos_de_valor.py | ✅ |
| Repuestos del Taller | infrastructure | repository | `RepositorioSolicitudDeReposicion` | id-766c6a84908053728dd7ac3f9a5060ae | services/repuestos-del-taller/src/repuestos_del_taller/adapters/outbound/persistencia.py | ✅ |
| Repuestos del Taller | infrastructure | cache_decorator | `RepositorioCacheadoSolicitudDeReposicion` | id-766c6a84908053728dd7ac3f9a5060ae | services/repuestos-del-taller/src/repuestos_del_taller/adapters/outbound/persistencia.py | ✅ |
| Repuestos del Taller | domain | domain_event | `RepuestoRecibido` | id-1be08aad92855cbaa7ff830b56c2037d | services/repuestos-del-taller/src/repuestos_del_taller/domain/existencias/eventos.py | ✅ |
| Repuestos del Taller | domain | domain_event | `RepuestoReservado` | id-186875460cb651eaa0dbf3e4cb2e0415 | services/repuestos-del-taller/src/repuestos_del_taller/domain/existencias/eventos.py | ✅ |
| Repuestos del Taller | domain | domain_event | `FaltanteDetectado` | id-2cf3752dc1d4514094ea591152da372e | services/repuestos-del-taller/src/repuestos_del_taller/domain/existencias/eventos.py | ✅ |
| Repuestos del Taller | domain | domain_event | `ReservaLiberada` | id-a83e35654a595b949cbd23b300a91c88 | services/repuestos-del-taller/src/repuestos_del_taller/domain/existencias/eventos.py | ✅ |
| Repuestos del Taller | domain | domain_event | `ConsumoConfirmado` | id-f779e6203134532591917e8df0d8cc33 | services/repuestos-del-taller/src/repuestos_del_taller/domain/existencias/eventos.py | ✅ |
| Repuestos del Taller | domain | domain_event | `StockMinimoAlcanzado` | id-d67cad9cf45b5c44ab04faf0a4fdd9a6 | services/repuestos-del-taller/src/repuestos_del_taller/domain/existencias/eventos.py | ✅ |
| Repuestos del Taller | domain | domain_event | `ExistenciaAjustada` | id-a64d9b289ef85b318761fa6317d4e85e | services/repuestos-del-taller/src/repuestos_del_taller/domain/existencias/eventos.py | ✅ |
| Repuestos del Taller | domain | domain_event | `ReposicionSolicitada` | id-542ae652fb715e74b5ef68833a6dd13f | services/repuestos-del-taller/src/repuestos_del_taller/domain/reposicion/eventos.py | ✅ |
| Repuestos del Taller | domain | domain_event | `SolicitudAprobada` | id-7e039a997d34537aaf3a679a10ccbf75 | services/repuestos-del-taller/src/repuestos_del_taller/domain/reposicion/eventos.py | ✅ |
| Repuestos del Taller | domain | domain_event | `SolicitudCancelada` | id-21dd0913e6715f7fa9513fcab0ab36c1 | services/repuestos-del-taller/src/repuestos_del_taller/domain/reposicion/eventos.py | ✅ |
| Repuestos del Taller | domain | business_rule | `ExistenciaInsuficiente` | EXISTENCIA_INSUFICIENTE | services/repuestos-del-taller/src/repuestos_del_taller/domain/existencias/reglas.py | ✅ |
| Repuestos del Taller | domain | business_rule | `ReferenciaInexistente` | REFERENCIA_INEXISTENTE | services/repuestos-del-taller/src/repuestos_del_taller/domain/existencias/reglas.py | ✅ |
| Repuestos del Taller | domain | business_rule | `SolicitudAbierta` | SOLICITUD_ABIERTA | services/repuestos-del-taller/src/repuestos_del_taller/domain/reposicion/reglas.py | ✅ |
| Repuestos del Taller | application | command | `RegistrarEntradaDeRepuestoComando` | id-ccd5d1d7a7fe5f779b5401335b383c70 | services/repuestos-del-taller/src/repuestos_del_taller/application/comandos.py | ✅ |
| Repuestos del Taller | application | command_handler | `RegistrarEntradaDeRepuestoManejador` | id-ccd5d1d7a7fe5f779b5401335b383c70 | services/repuestos-del-taller/src/repuestos_del_taller/application/manejadores.py | ✅ |
| Repuestos del Taller | application | validator | `RegistrarEntradaDeRepuestoValidador` | id-ccd5d1d7a7fe5f779b5401335b383c70 | services/repuestos-del-taller/src/repuestos_del_taller/application/validadores.py | ✅ |
| Repuestos del Taller | api | request_model | `RegistrarEntradaDeRepuestoSolicitud` | id-ccd5d1d7a7fe5f779b5401335b383c70 | services/repuestos-del-taller/src/repuestos_del_taller/adapters/inbound/http/modelos.py | ✅ |
| Repuestos del Taller | tests | test | `RegistrarEntradaDeRepuestoComando` | id-ccd5d1d7a7fe5f779b5401335b383c70 | services/repuestos-del-taller/tests/test_revision.py | ✅ |
| Repuestos del Taller | application | command | `ReservarRepuestoComando` | id-4457c290e41a519496b5673da746dc04 | services/repuestos-del-taller/src/repuestos_del_taller/application/comandos.py | ✅ |
| Repuestos del Taller | application | command_handler | `ReservarRepuestoManejador` | id-4457c290e41a519496b5673da746dc04 | services/repuestos-del-taller/src/repuestos_del_taller/application/manejadores.py | ✅ |
| Repuestos del Taller | application | validator | `ReservarRepuestoValidador` | id-4457c290e41a519496b5673da746dc04 | services/repuestos-del-taller/src/repuestos_del_taller/application/validadores.py | ✅ |
| Repuestos del Taller | api | request_model | `ReservarRepuestoSolicitud` | id-4457c290e41a519496b5673da746dc04 | services/repuestos-del-taller/src/repuestos_del_taller/adapters/inbound/http/modelos.py | ✅ |
| Repuestos del Taller | tests | test | `ReservarRepuestoComando` | id-4457c290e41a519496b5673da746dc04 | services/repuestos-del-taller/tests/test_revision.py | ✅ |
| Repuestos del Taller | application | command | `LiberarReservaComando` | id-71639f81a7d15643b5004c9e7be7d0d3 | services/repuestos-del-taller/src/repuestos_del_taller/application/comandos.py | ✅ |
| Repuestos del Taller | application | command_handler | `LiberarReservaManejador` | id-71639f81a7d15643b5004c9e7be7d0d3 | services/repuestos-del-taller/src/repuestos_del_taller/application/manejadores.py | ✅ |
| Repuestos del Taller | application | validator | `LiberarReservaValidador` | id-71639f81a7d15643b5004c9e7be7d0d3 | services/repuestos-del-taller/src/repuestos_del_taller/application/validadores.py | ✅ |
| Repuestos del Taller | api | request_model | `LiberarReservaSolicitud` | id-71639f81a7d15643b5004c9e7be7d0d3 | services/repuestos-del-taller/src/repuestos_del_taller/adapters/inbound/http/modelos.py | ✅ |
| Repuestos del Taller | tests | test | `LiberarReservaComando` | id-71639f81a7d15643b5004c9e7be7d0d3 | services/repuestos-del-taller/tests/test_adaptadores.py | ✅ |
| Repuestos del Taller | application | command | `ConfirmarConsumoComando` | id-f414f0d49cb55d5c82f5ca2fcf9f010e | services/repuestos-del-taller/src/repuestos_del_taller/application/comandos.py | ✅ |
| Repuestos del Taller | application | command_handler | `ConfirmarConsumoManejador` | id-f414f0d49cb55d5c82f5ca2fcf9f010e | services/repuestos-del-taller/src/repuestos_del_taller/application/manejadores.py | ✅ |
| Repuestos del Taller | application | validator | `ConfirmarConsumoValidador` | id-f414f0d49cb55d5c82f5ca2fcf9f010e | services/repuestos-del-taller/src/repuestos_del_taller/application/validadores.py | ✅ |
| Repuestos del Taller | api | request_model | `ConfirmarConsumoSolicitud` | id-f414f0d49cb55d5c82f5ca2fcf9f010e | services/repuestos-del-taller/src/repuestos_del_taller/adapters/inbound/http/modelos.py | ✅ |
| Repuestos del Taller | tests | test | `ConfirmarConsumoComando` | id-f414f0d49cb55d5c82f5ca2fcf9f010e | services/repuestos-del-taller/tests/test_revision.py | ✅ |
| Repuestos del Taller | application | command | `AjustarExistenciaPorConteoComando` | id-e2ab33f62f83589d89a543f7fd6298ff | services/repuestos-del-taller/src/repuestos_del_taller/application/comandos.py | ✅ |
| Repuestos del Taller | application | command_handler | `AjustarExistenciaPorConteoManejador` | id-e2ab33f62f83589d89a543f7fd6298ff | services/repuestos-del-taller/src/repuestos_del_taller/application/manejadores.py | ✅ |
| Repuestos del Taller | application | validator | `AjustarExistenciaPorConteoValidador` | id-e2ab33f62f83589d89a543f7fd6298ff | services/repuestos-del-taller/src/repuestos_del_taller/application/validadores.py | ✅ |
| Repuestos del Taller | api | request_model | `AjustarExistenciaPorConteoSolicitud` | id-e2ab33f62f83589d89a543f7fd6298ff | services/repuestos-del-taller/src/repuestos_del_taller/adapters/inbound/http/modelos.py | ✅ |
| Repuestos del Taller | tests | test | `AjustarExistenciaPorConteoComando` | id-e2ab33f62f83589d89a543f7fd6298ff | services/repuestos-del-taller/tests/test_adaptadores.py | ✅ |
| Repuestos del Taller | application | command | `SolicitarReposicionComando` | id-ba820033885b5e5c8de028b7d471ac2f | services/repuestos-del-taller/src/repuestos_del_taller/application/comandos.py | ✅ |
| Repuestos del Taller | application | command_handler | `SolicitarReposicionManejador` | id-ba820033885b5e5c8de028b7d471ac2f | services/repuestos-del-taller/src/repuestos_del_taller/application/manejadores.py | ✅ |
| Repuestos del Taller | application | validator | `SolicitarReposicionValidador` | id-ba820033885b5e5c8de028b7d471ac2f | services/repuestos-del-taller/src/repuestos_del_taller/application/validadores.py | ✅ |
| Repuestos del Taller | api | request_model | `SolicitarReposicionSolicitud` | id-ba820033885b5e5c8de028b7d471ac2f | services/repuestos-del-taller/src/repuestos_del_taller/adapters/inbound/http/modelos.py | ✅ |
| Repuestos del Taller | tests | test | `SolicitarReposicionComando` | id-ba820033885b5e5c8de028b7d471ac2f | services/repuestos-del-taller/tests/test_adaptadores.py | ✅ |
| Repuestos del Taller | application | command | `AprobarSolicitudComando` | id-419859743da258ec9e9e5edf83faf4ce | services/repuestos-del-taller/src/repuestos_del_taller/application/comandos.py | ✅ |
| Repuestos del Taller | application | command_handler | `AprobarSolicitudManejador` | id-419859743da258ec9e9e5edf83faf4ce | services/repuestos-del-taller/src/repuestos_del_taller/application/manejadores.py | ✅ |
| Repuestos del Taller | application | validator | `AprobarSolicitudValidador` | id-419859743da258ec9e9e5edf83faf4ce | services/repuestos-del-taller/src/repuestos_del_taller/application/validadores.py | ✅ |
| Repuestos del Taller | api | request_model | `AprobarSolicitudSolicitud` | id-419859743da258ec9e9e5edf83faf4ce | services/repuestos-del-taller/src/repuestos_del_taller/adapters/inbound/http/modelos.py | ✅ |
| Repuestos del Taller | tests | test | `AprobarSolicitudComando` | id-419859743da258ec9e9e5edf83faf4ce | services/repuestos-del-taller/tests/test_revision.py | ✅ |
| Repuestos del Taller | application | command | `CancelarSolicitudComando` | id-c8dbdeffe37751e7b00d73efc5c5c9c9 | services/repuestos-del-taller/src/repuestos_del_taller/application/comandos.py | ✅ |
| Repuestos del Taller | application | command_handler | `CancelarSolicitudManejador` | id-c8dbdeffe37751e7b00d73efc5c5c9c9 | services/repuestos-del-taller/src/repuestos_del_taller/application/manejadores.py | ✅ |
| Repuestos del Taller | application | validator | `CancelarSolicitudValidador` | id-c8dbdeffe37751e7b00d73efc5c5c9c9 | services/repuestos-del-taller/src/repuestos_del_taller/application/validadores.py | ✅ |
| Repuestos del Taller | api | request_model | `CancelarSolicitudSolicitud` | id-c8dbdeffe37751e7b00d73efc5c5c9c9 | services/repuestos-del-taller/src/repuestos_del_taller/adapters/inbound/http/modelos.py | ✅ |
| Repuestos del Taller | tests | test | `CancelarSolicitudComando` | id-c8dbdeffe37751e7b00d73efc5c5c9c9 | services/repuestos-del-taller/tests/test_adaptadores.py | ✅ |
| Repuestos del Taller | contracts | published_contract | `FaltanteDetectadoV1` | Faltante detectado | services/repuestos-del-taller/src/repuestos_del_taller/contracts/eventos.py | ✅ |
| Repuestos del Taller | application | event_translator | `FaltanteDetectadoTraductor` | Faltante detectado | services/repuestos-del-taller/src/repuestos_del_taller/application/integracion.py | ✅ |
| Repuestos del Taller | contracts | topics | `RepuestosDelTallerTopicos` | Repuestos del Taller | services/repuestos-del-taller/src/repuestos_del_taller/contracts/topicos.py | ✅ |
| Repuestos del Taller | application | event_consumer | `ParadaProgramadaConsumidor` | Parada programada | services/repuestos-del-taller/src/repuestos_del_taller/application/integracion.py | ✅ |
| Repuestos del Taller | application | event_consumer | `OrdenDeTrabajoCerradaConsumidor` | Orden de trabajo cerrada | services/repuestos-del-taller/src/repuestos_del_taller/application/integracion.py | ✅ |
| Repuestos del Taller | application | policy_observer | `StockMinimoAlcanzadoObservador` | Stock mínimo alcanzado | services/repuestos-del-taller/src/repuestos_del_taller/application/integracion.py | ✅ |
| Repuestos del Taller | application | acl_port | `IEnviarAviso` | Notificaciones | services/repuestos-del-taller/src/repuestos_del_taller/application/puertos.py | ✅ |
| Repuestos del Taller | infrastructure | acl_adapter | `EnviarAvisoAdapter` | Notificaciones | services/repuestos-del-taller/src/repuestos_del_taller/adapters/outbound/integracion.py | ✅ |
| Repuestos del Taller | application | crypto_port | `Cifrador` |  | services/repuestos-del-taller/src/repuestos_del_taller/application/puertos.py | ✅ |
| Repuestos del Taller | infrastructure | crypto_impl | `CifradorAes` |  | services/repuestos-del-taller/src/repuestos_del_taller/adapters/outbound/seguridad.py | ✅ |
| Repuestos del Taller | infrastructure | event_publisher | `PublicadorDeEventosHttp` |  | services/repuestos-del-taller/src/repuestos_del_taller/adapters/outbound/integracion.py | ✅ |
| Repuestos del Taller | api | endpoints | `RepuestosDelTallerEndpoints` | Repuestos del Taller | services/repuestos-del-taller/src/repuestos_del_taller/adapters/inbound/http/endpoints.py | ✅ |
| Repuestos del Taller | api | composition_root | `RepuestosDelTallerComposicion` | Repuestos del Taller | services/repuestos-del-taller/src/repuestos_del_taller/adapters/inbound/http/composicion.py | ✅ |
| Repuestos del Taller | infrastructure | infra_pattern | `BandejaDeSalida` |  | services/repuestos-del-taller/src/repuestos_del_taller/adapters/outbound/integracion.py | ✅ |
| Repuestos del Taller | infrastructure | infra_pattern | `ProcesadorDeMensajeEntrante` |  | services/repuestos-del-taller/src/repuestos_del_taller/adapters/outbound/integracion.py | ✅ |
| Repuestos del Taller | ops | file | `Dockerfile` |  | services/repuestos-del-taller/Dockerfile | ✅ |
| Repuestos del Taller | ops | file | `README.md` |  | services/repuestos-del-taller/README.md | ✅ |
| Repuestos del Taller | ops | file | `proyecto` |  | services/repuestos-del-taller/pyproject.toml | ✅ |
| Repuestos del Taller | api | route | `/api/existencia` | id-ccd5d1d7a7fe5f779b5401335b383c70 | services/repuestos-del-taller/src/repuestos_del_taller/adapters/inbound/http/endpoints.py | ✅ |
| Repuestos del Taller | api | route | `reservar-repuesto` | id-4457c290e41a519496b5673da746dc04 | services/repuestos-del-taller/src/repuestos_del_taller/adapters/inbound/http/endpoints.py | ✅ |
| Repuestos del Taller | api | route | `liberar-reserva` | id-71639f81a7d15643b5004c9e7be7d0d3 | services/repuestos-del-taller/src/repuestos_del_taller/adapters/inbound/http/endpoints.py | ✅ |
| Repuestos del Taller | api | route | `confirmar-consumo` | id-f414f0d49cb55d5c82f5ca2fcf9f010e | services/repuestos-del-taller/src/repuestos_del_taller/adapters/inbound/http/endpoints.py | ✅ |
| Repuestos del Taller | api | route | `ajustar-existencia-por-conteo` | id-e2ab33f62f83589d89a543f7fd6298ff | services/repuestos-del-taller/src/repuestos_del_taller/adapters/inbound/http/endpoints.py | ✅ |
| Repuestos del Taller | api | route | `/api/solicitud-de-reposicion` | id-ba820033885b5e5c8de028b7d471ac2f | services/repuestos-del-taller/src/repuestos_del_taller/adapters/inbound/http/endpoints.py | ✅ |
| Repuestos del Taller | api | route | `aprobar-solicitud` | id-419859743da258ec9e9e5edf83faf4ce | services/repuestos-del-taller/src/repuestos_del_taller/adapters/inbound/http/endpoints.py | ✅ |
| Repuestos del Taller | api | route | `cancelar-solicitud` | id-c8dbdeffe37751e7b00d73efc5c5c9c9 | services/repuestos-del-taller/src/repuestos_del_taller/adapters/inbound/http/endpoints.py | ✅ |
| Repuestos del Taller | frontend | form | `RegistrarEntradaDeRepuestoForm` | Registrar entrada de repuesto | frontend/mfe-repuestos-del-taller/src/forms/RegistrarEntradaDeRepuestoForm.tsx | ✅ |
| Repuestos del Taller | frontend | form | `LiberarReservaForm` | Liberar reserva | frontend/mfe-repuestos-del-taller/src/forms/LiberarReservaForm.tsx | ✅ |
| Repuestos del Taller | frontend | form | `AjustarExistenciaPorConteoForm` | Ajustar existencia por conteo | frontend/mfe-repuestos-del-taller/src/forms/AjustarExistenciaPorConteoForm.tsx | ✅ |
| Repuestos del Taller | frontend | form | `AprobarSolicitudForm` | Aprobar solicitud | frontend/mfe-repuestos-del-taller/src/forms/AprobarSolicitudForm.tsx | ✅ |
| Repuestos del Taller | frontend | form | `CancelarSolicitudForm` | Cancelar solicitud | frontend/mfe-repuestos-del-taller/src/forms/CancelarSolicitudForm.tsx | ✅ |
