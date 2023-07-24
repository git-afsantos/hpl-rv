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


// -----------------------------------------------------------------------------
//  Components
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
    }
  },
};


const LiveServerList = {
  template: "#vue-live-server-list",

  emits: ["show-dialog"],

  data() {
    return {
      servers: [],
    };
  },

  methods: {
    showConnectionDialog() {
      this.$emit("show-dialog");
    },
  },
};


const RuntimeMonitorList = {
  template: "#vue-runtime-monitor-list",

  data() {
    return {
      monitors: [],
    };
  }
};


const RuntimeMonitor = {
  template: "#vue-runtime-monitor",

  props: {
    name: String,
    property: String,
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
    }
  }
};


// -----------------------------------------------------------------------------
//  Application
// -----------------------------------------------------------------------------

const app = createApp({
  template: "#vue-dashboard",

  data() {
    return {
      openModals: 0,
    };
  },

  computed: {
    isModalOpen() {
      return this.openModals > 0;
    }
  },

  methods: {
    onSetupDone() {},

    showConnectionDialog() {
      this.$refs.connectionDialog.show();
    },

    connectToLiveMonitor(host, port) {
      postData("/live", { host, port })
      .then(() => alert("Connected to server!"))
      .catch((reason) => alert(`Error: ${reason}`));
    },

    onModalOpened() {
      this.openModals += 1;
    },

    onModalClosed() {
      this.openModals = Math.max(0, this.openModals - 1);
    },
  },

  mounted() {}
});
  
  
// -----------------------------------------------------------------------------
//  Setup
// -----------------------------------------------------------------------------
  
app.component("ConnectionDialog", ConnectionDialog);
app.component("LiveServerList", LiveServerList);
app.component("RuntimeMonitorList", RuntimeMonitorList);
app.component("RuntimeMonitor", RuntimeMonitor);

app.mount("#app");