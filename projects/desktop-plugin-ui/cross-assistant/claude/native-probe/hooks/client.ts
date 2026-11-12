// A Client draws native elements on a drawing thread. It has no mods API.
export default function ClientProbe(props, surface) {
  if (surface.state === undefined) {
    surface.setState({ key: "none", pointer: "none", ticks: 0 });
    surface.every(1000, () => surface.setState({ ...surface.state, ticks: surface.state.ticks + 1 }));
  }
  surface.onKey(event => surface.setState({ ...surface.state, key: event.key }));
  surface.onPointer(event => surface.setState({ ...surface.state, pointer: `${event.type}:${event.x},${event.y}` }));
  const { Box, Text, Button } = surface.elements;
  const state = surface.state ?? { key: "none", pointer: "none", ticks: 0 };
  return Box({ flexDirection: "column", children: [
    Text({ children: `Label: ${props.label}` }),
    Text({ children: `Key: ${state.key}` }),
    Text({ children: `Pointer: ${state.pointer}` }),
    Text({ children: `Ticks: ${state.ticks}` }),
    Text({ children: `Size: ${surface.columns}x${surface.rows}` }),
    Button({ key: "client-post", label: "Update through hooks", onPress: () => surface.post({ label: "From client" }) }),
  ] });
}
