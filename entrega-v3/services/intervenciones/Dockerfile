FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /app
COPY . .
RUN dotnet publish src/Intervenciones.Api/Intervenciones.Api.csproj -c Release -o /out

FROM mcr.microsoft.com/dotnet/aspnet:8.0
WORKDIR /app
COPY --from=build /out .
ENV PORT=5101
EXPOSE 5101
ENTRYPOINT ["dotnet", "Intervenciones.Api.dll"]
