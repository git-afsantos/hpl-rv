// SPDX-License-Identifier: MIT
// Copyright © 2023 André Santos

// -----------------------------------------------------------------------------
//  Constants
// -----------------------------------------------------------------------------

const { createApp } = Vue;

const PROPERTY_KEYWORDS = [
  /(^|\s)(globally)(\s*:)/ig,
  /(^|\s)(after)(\s+\S)/ig,
  /(^|\s)(until)(\s+\S)/ig,
  /(:\s*)(no)(\s)/ig,
  /(:\s*)(some)(\s)/ig,
  /(\S\s+)(causes)(\s+\S)/ig,
  /(\S\s+)(requires)(\s+\S)/ig,
  /(\S\s+)(forbids)(\s+\S)/ig,
  /(\S\s+)(or)(\s+\S)/ig,
  /(\S\s+)(within)(\s+\d)/ig,
  /(\d\s*)(s)(\s|$)/ig,
  /(\d\s*)(ms)(\s|$)/ig,
];

const PREDICATE_KEYWORDS = [
  /(\W)(not)(\s)/ig,
  /(\s)(and)(\s)/ig,
  /(\s)(or)(\s)/ig,
  /(\s)(implies)(\s)/ig,
  /(\s)(in)(\s)/ig,
];

const PREDICATE_REGEX = /(\S\s*)(\{.*?\})/g;
const CHANNEL_REGEX = /(:|\s)([a-zA-Z_\-/$#?][\w-/$#?]*)(\s|\{|$)/g;
const NUMBER_REGEX = /(\D)(\d*\.?\d+)(\D)/g;
const STRING_REGEX = /("(?:\\?[\S\s])*?")/g;
const BOOLEAN_REGEX = /(\W)(true|false)(\W)/ig;

// -----------------------------------------------------------------------------
//  Utility
// -----------------------------------------------------------------------------


async function postData(url = "", data = {}) {
  // Default options are marked with *
  const response = await fetch(url, {
    method: "POST",
    // mode: "cors", // no-cors, *cors, same-origin
    cache: "no-cache",
    // credentials: "same-origin",
    headers: {
      "Content-Type": "application/json",  // application/x-www-form-urlencoded
    },
    // redirect: "follow", // manual, *follow, error
    // referrerPolicy: "no-referrer", // no-referrer, *no-referrer-when-downgrade, origin, origin-when-cross-origin, same-origin, strict-origin, strict-origin-when-cross-origin, unsafe-url
    body: JSON.stringify(data),
  });
  if (response.ok) {
    return response.json();
  }
  return response.json().then((data) => {
    const error = new Error(response.status);
    error.response = data;
    error.status = response.status;
    throw error;
  });
}


function padWithMonitors(monitors, n) {
  while (monitors.length < n) {
    const i = monitors.length + 1;
    monitors.push({
      id: `p${i}`,
      title: `Property ${i}`,
      property: "",
      verdict: null,
      witness: [],
    });
  }
}


// -----------------------------------------------------------------------------
//  Generic Components
// -----------------------------------------------------------------------------


const ConnectionDialog = {
  template: "#vue-connection-dialog",

  emits: ["modal-opened", "modal-closed", "connect-to-server"],

  data() {
    return {
      host: "127.0.0.1",
      port: 4242,
    };
  },

  computed: {
    isOpen() {
      return this.$refs.dialog.open;
    }
  },

  methods: {
    show() {
      if (!this.isOpen) {
        this.$refs.dialog.showModal();
        this.$emit("modal-opened");
      }
    },

    cancelDialog() {
      this.$refs.dialog.close();
      this.$emit("modal-closed");
    },

    connectToLiveMonitor() {
      this.$emit("modal-closed");
      this.$emit("connect-to-server", this.host, this.port);
      this.$refs.dialog.close();
    }
  },
};


const WitnessDialog = {
  template: "#vue-witness-dialog",

  emits: ["modal-opened", "modal-closed"],

  data() { return { witness: [] } },

  computed: {
    isOpen() { return this.$refs.dialog.open }
  },

  methods: {
    show(witness) {
      this.witness = witness || [];
      if (!this.isOpen) {
        this.$refs.dialog.showModal();
        this.$emit("modal-opened");
      }
    },

    cancelDialog() {
      this.$refs.dialog.close();
      this.$emit("modal-closed");
    }
  }
};


// -----------------------------------------------------------------------------
//  Live Server Components
// -----------------------------------------------------------------------------


const LiveServerList = {
  template: "#vue-live-server-list",

  emits: ["show-dialog", "select-server", "close-server"],

  props: {
    servers: {
      type: Array,
      default(_rawProps) { return [] },
    },
    selection: Number,
  },

  methods: {
    onUserSelect(host, port) {
      this.$emit("select-server", host, port);
    },

    onCloseConnection(host, port) {
      this.$emit("close-server", host, port);
    },

    showConnectionDialog() {
      this.$emit("show-dialog");
    },
  },
};


const LiveServer = {
  template: "#vue-live-server",

  emits: ["user-select", "close"],

  props: {
    host: String,
    port: Number,
    monitors: {
      type: Array,
      default(_rawProps) { return [] }
    },
    isSelected: Boolean,
    isOnline: Boolean,
  },

  computed: {
    numMonitors() {
      const n = this.monitors.length;
      return n === 1 ? "1 monitor" : `${n} monitors`;
    },

    statusClass() {
      return this.isOnline ? "online" : "offline";
    },

    statusIcon() {
      return this.isOnline ? "O" : "X";
    }
  },

  methods: {
    onSelect() {
      if (!this.isSelected) {
        this.$emit("user-select", this.host, this.port);
      }
    },

    onCloseConnection() {
      this.$emit("close", this.host, this.port);
    },
  }
};


// -----------------------------------------------------------------------------
//  Runtime Monitor Components
// -----------------------------------------------------------------------------


const RuntimeMonitorList = {
  template: "#vue-runtime-monitor-list",

  emits: ["show-witness"],

  props: {
    monitors: {
      type: Array,
      default(_rawProps) { return [] },
    }
  },

  methods: {
    showWitness(witness) {
      this.$emit("show-witness", witness);
    }
  }
};


const RuntimeMonitor = {
  template: "#vue-runtime-monitor",

  emits: ["show-witness"],

  props: {
    title: String,
    property: String,
    verdict: Boolean,
    witness: Array,
  },

  computed: {
    propertyHTML() {
      // replace predicates with placeholders
      let p = this.property.replace(PREDICATE_REGEX, "$1{}");
      // bolden keywords in the scope and pattern structures
      for (const re of PROPERTY_KEYWORDS) {
        p = p.replace(re, "$1<b>$2</b>$3");
      }
      // colorize channel names
      p = p.replace(CHANNEL_REGEX, '$1<span class="special">$2</span>$3');
      // handle predicates
      const matches = [...this.property.matchAll(PREDICATE_REGEX)];
      for (const match of matches) {
        let predicate = match[2];
        // replace strings with placeholders
        const strings = [...predicate.matchAll(STRING_REGEX)];
        predicate = predicate.replace(STRING_REGEX, '""');
        // bolden predicate keywords
        for (const re of PREDICATE_KEYWORDS) {
          predicate = predicate.replace(re, "$1<b>$2</b>$3");
        }
        // colorize booleans
        predicate = predicate.replace(BOOLEAN_REGEX, '$1<span class="bool">$2</span>$3');
        // put colorized strings back in place
        for (const s of strings) {
          // replace just one string at a time, in order
          predicate = predicate.replace('""', `<span class="string">${s[0]}</span>`);
        }
        // replace just one predicate at a time in the global property
        p = p.replace("{}", predicate);
      }
      // colorize numbers
      p = p.replace(NUMBER_REGEX, '$1<span class="number">$2</span>$3');
      return p;
    },

    statusClass() {
      if (this.verdict === true) { return "success" }
      if (this.verdict === false) { return "failure" }
      return "";
    },

    statusIcon() {
      if (this.verdict === true) { return "T" }
      if (this.verdict === false) { return "F" }
      return "?";
    }
  },

  methods: {
    showWitness() {
      if (this.witness == null) { return }
      this.$emit("show-witness", this.witness);
    }
  }
};


// -----------------------------------------------------------------------------
//  Main Application
// -----------------------------------------------------------------------------

const app = createApp({
  template: "#vue-dashboard",

  data() {
    return {
      openModals: 0,
      servers: [],
      selectedServer: null,
      websocket: null,
    };
  },

  computed: {
    isModalOpen() {
      return this.openModals > 0;
    },

    displayedMonitors() {
      if (this.selectedServer == null) { return [] }
      const server = this.servers[this.selectedServer];
      if (server == null) { return [] }
      return server.monitors;
    }
  },

  methods: {
    onSetupDone() {},

    onServerSelected(host, port) {
      for (const i of this.servers.keys()) {
        const server = this.servers[i];
        if (server.host !== host) { continue }
        if (server.port !== port) { continue }
        this.selectedServer = i;
        // this.displayedMonitors = server.monitors;
        return;
      }
    },

    onServerClosed(host, port) {
      for (const i of this.servers.keys()) {
        const server = this.servers[i];
        if (server.host !== host) { continue }
        if (server.port !== port) { continue }

        this.servers.splice(i, 1);

        if (this.selectedServer === i) {
          if (this.servers.length === 0) {
            this.selectedServer = null;
            // this.displayedMonitors = [];
          } else if (i >= this.servers.length) {
            // must have closed the last on the list
            this.selectedServer = this.servers.length - 1;
            // this.displayedMonitors = server.monitors;
          }
        } else if (this.selectedServer > i) {
          // removed one above the selected; shift by one
          this.selectedServer--;
        }

        if (this.servers.length === 0 && this.websocket != null) {
          this.websocket.close();
          this.websocket = null;
        }

        return;
      }
    },

    showWitnessDialog(witness) {
      this.$refs.witnessDialog.show(witness);
    },

    showConnectionDialog() {
      this.$refs.connectionDialog.show();
    },

    connectToLiveMonitor(host, port) {
      const self = this;
      postData("/live", { host, port })
      .then(data => {
        self.servers = [];
        for (const server of data.servers) {
          console.log("register new live server", server);
          self.servers.push({ host: server.host, port: server.port, monitors: [] });
        }
        if (self.servers.length > 0) {
          self.selectedServer = 0;
        }
        console.log("server list", self.servers);
        if (self.websocket == null) {
          self.websocket = new WebSocket(`ws://${window.location.host}/ws`);
          self.websocket.onmessage = event => self.onMonitorUpdate(JSON.parse(event.data));
          self.websocket.onclose = () => { self.websocket = null };
        }
      })
      .catch((reason) => alert(`Error: ${reason}`));
    },

    disconnectFromLiveMonitor(server) {
      console.log("disconnected");
    },

    onMonitorUpdate(msg) {
      console.log("message from live server", msg);
      for (const server of this.servers) {
        const addr = `${server.host}:${server.port}`;
        if (addr !== msg.server) { continue }

        const i = msg.id;
        padWithMonitors(server.monitors, i+1);
        server.monitors[i] = msg.monitor;
        return;
      }
    },

    onModalOpened() {
      this.openModals += 1;
    },

    onModalClosed() {
      this.openModals = Math.max(0, this.openModals - 1);
    },
  },

  mounted() {
    if (this.servers.length > 0) {
      this.selectedServer = 0;
      // this.displayedMonitors = this.servers[this.selectedServer].monitors;
    }
  }
});


// -----------------------------------------------------------------------------
//  Setup
// -----------------------------------------------------------------------------

app.component("ConnectionDialog", ConnectionDialog);
app.component("WitnessDialog", WitnessDialog);
app.component("LiveServerList", LiveServerList);
app.component("LiveServer", LiveServer);
app.component("RuntimeMonitorList", RuntimeMonitorList);
app.component("RuntimeMonitor", RuntimeMonitor);

app.mount("#app");


// -----------------------------------------------------------------------------
//  Testing
// -----------------------------------------------------------------------------


function exampleServers() {
  return [
    {
      host: "127.0.0.1",
      port: 4242,
      monitors: [{
        id: "p1",
        title: "Property 1",
        property: "globally: /a {true} causes /b {(not x and y and z) implies w} within 100 ms",
        verdict: true,
        witness: [],
      }, {
        id: "p2",
        title: "Property 2",
        property: 'after /chat {msg = "hello"}: some /chat {msg = "world"} within .1s',
        verdict: false,
        witness: [],
      }],
    },
    {
      host: "127.0.0.1",
      port: 5176,
      monitors: [{
        id: "p3",
        title: "Property 3",
        property: 'until /chat {msg = "false"}: some /true {value = true}',
        verdict: null,
      }],
    },
    {
      host: "127.0.0.1",
      port: 8080,
      monitors: [],
    },
  ];
}
