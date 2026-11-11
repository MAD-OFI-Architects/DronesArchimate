using BuildingBlocks.Api.DependencyInjection;
using BuildingBlocks.Infrastructure.DependencyInjection;
using Intervenciones.Api;

var opciones = OpcionesDeMicroservicio.DesdeEntorno("intervenciones");
var builder = WebApplication.CreateBuilder(args);
builder.WebHost.UseUrls($"http://0.0.0.0:{opciones.Puerto}");
builder.Services.AgregarIntervenciones(opciones);

var app = builder.Build();
app.UsarBloquesDeApi();
app.MapearModulosDeEndpoints();
app.Run();
