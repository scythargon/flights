import React, {useState} from 'react';
import {FeatureGroup, MapContainer, Marker, Polyline, Tooltip, TileLayer} from 'react-leaflet';
import {map, when, propEq, assoc} from "ramda";
import styled from "styled-components";

import L, {Icon as LeafletIcon} from "leaflet";

import 'leaflet/dist/leaflet.css';
import iconImg from "./static/marker-icon.png";

const alter = (keyField, keyEquals, valueField, valueEquals) => map(
  when(propEq(keyField, keyEquals), assoc(valueField, valueEquals)),
);


const icon = new LeafletIcon({
  iconUrl: iconImg,
  shadowSize: [50, 64],
  shadowAnchor: [4, 62],
  iconAnchor: [12, 40],
});

export const customMarkerUserPos = new L.Icon({
  iconUrl: "https://unpkg.com/leaflet@1.5.1/dist/images/marker-icon.png",
  iconSize: [15, 20],
  iconAnchor: [5, 20],
  popupAnchor: [2, -40]
});


const MyMap = () => {
  const [markers, setMarkers] = useState([
    // {lat: -8.4095184, lng: 115.188916, code: 'DPS', loaded: false, linesEnabled: false, visible: true},
    {lat: 55.033, lng: 82.933, code: 'OVB', loaded: false, linesEnabled: false, visible: true},
    {lat: 27.2579, lng: 33.8116, code: 'HRG', loaded: false, linesEnabled: false, visible: true},
    // {code: "TCI", "lat": 28.2915637, "lng": -16.6291304, loaded: false, linesEnabled: false, visible: true}
  ]);

  const [lines, setLines] = useState([]);

  const [config, setConfig] = useState({showDanglingCities: true});

  const markerClick = (marker) => {
    if (marker.loaded) {
      const changedMarkers = alter('code', marker.code, 'linesEnabled', !marker.linesEnabled)(markers);

      const newLines = lines.map(line => {
        if (line.source === marker.code) {
          line.enabled = !marker.linesEnabled;
          line.selected = false;
        }
        return line;
      });
      setMarkers(changedMarkers);
      setLines(newLines);
    } else {
      fetch(`http://127.0.0.1:8000/api/marker?origin=${marker.code}`)
        .then(response => response.json())
        .then(data => {
          const knownCities = markers.map(m => m.code);
          const newMarkers = data.filter(price => !knownCities.includes(price.iata)).map(price => ({
            lat: price.lat,
            lng: price.lng,
            code: price.iata,
            loaded: false,
            linesEnabled: false,
            visible: true
          }));

          const newLines = data.map(price => ({
            source: marker.code,
            dest: price.iata,
            enabled: true,
            selected: false,
            leg: [
              [marker.lat, marker.lng],
              [price.lat, price.lng]
            ]
          }));
          let changedMarkers = alter('code', marker.code, 'loaded', true)(
            alter('code', marker.code, 'linesEnabled', true)(markers)
          );
          setMarkers([...changedMarkers, ...newMarkers]);
          setLines([...lines, ...newLines]);
        })
        .catch(error => console.log(error));
    }
  };

  const selectLine = (line) => {
    const wasSelected = line.selected;
    // alter(markers, 'code', line.source, 'linesEnabled', wasSelected);
    let changedMarkers = markers.map(m => ({
      ...m,
      visible: m.code !== line.source && m.code !== line.dest ? wasSelected : m.visible
    }));
    const changedLines = lines.map(l => {
      if (l.source === line.source && l.dest === line.dest) {
        l.selected = !l.selected;
      } else if (l.source === line.source) {
        l.enabled = wasSelected;
        changedMarkers = alter(changedMarkers, 'code', l.dest, 'visible', wasSelected);
      }
      return l;
    });
    setLines(changedLines);
    setMarkers(changedMarkers);
  };

  const toggleCities = () => {
    const newValue = !config.showDanglingCities;
    const changedMarkers = markers.map(c => {
      if (!lines.filter(l => l.source === c.code && l.enabled).length && !lines.filter(l => l.dest === c.code && l.enabled).length) {
        c.visible = newValue;
      }
      return c;
    });
    setMarkers(changedMarkers);
    setConfig(config => ({...config, showDanglingCities: newValue}));
  }

  return (
    <MapContainer center={[30, 80]} zoom={4} maxZoom={10}>
      <FeatureGroup>
        {lines.map((line, idx) => (
          line.enabled && <Polyline positions={line.leg} color="blue" opacity={0.3} key={idx} eventHandlers={{
            click: () => selectLine(line),
          }}/>
        ))}
      </FeatureGroup>
      <TileLayer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        attribution="Map data &copy; OpenStreetMap contributors"
      />
      {markers.map((marker, idx) => (
        marker.visible && <Marker key={idx} position={[marker.lat, marker.lng]} icon={icon} code={marker.code}
                                  eventHandlers={{
                                    click: () => markerClick(marker),
                                  }}
        >
          <Tooltip>{marker.code}</Tooltip>
        </Marker>
      ))}
      <ToggleButton onClick={toggleCities}>
        Toggle
      </ToggleButton>
    </MapContainer>
  );
}

const ToggleButton = styled.button`
  display: flex;
  align-items: center;
  position: absolute;
  top: 20px;
  right: 20px;
  width: 50px;
  height: 50px;
  background-color: white;
  border-radius: 5px;
  border-color: gray;
  border-style: solid;
  border-width: 1px 1px 1px 1px;
  opacity: 0.6;
  text-align: center;
  z-index: 500;

  &:hover {
    opacity: 0.8;
    cursor: pointer;
  }
`;

export default MyMap;