// frontend/src/vue-cal.d.ts
//
// vue-cal types — what TypeScript knows of the calendar component
// ─────────────────────────────────────────────────────────────────────────────
// vue-cal 4 ships no type file: without this one, the strict checks refuse
// its import ("could not find a declaration file"). It is declared as a
// Vue component taking any props, which vue-cal itself checks at run time;
// the events it gives back are typed where AppointmentsPage reads them.

declare module "vue-cal" {
  import type { DefineComponent } from "vue";

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const VueCal: DefineComponent<any, any, any>;
  export default VueCal;
}
