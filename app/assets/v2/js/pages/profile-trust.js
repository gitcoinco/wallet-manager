Vue.component('sms-verify-modal', {
  delimiters: [ '[[', ']]' ],
  data: function() {
    return {
      csrf: $("input[name='csrfmiddlewaretoken']").val(),
      validationStep: 'intro',
      phone: '',
      validNumber: false,
      errorMessage: '',
      verified: document.verified,
      code: '',
      timePassed: 0,
      timeInterval: 0,
      display_email_option: false,
      countDownActive: false
    };
  },
  props: {
    showValidation: {
      type: Boolean,
      required: false,
      'default': false
    }
  },
  template: `<b-modal id="sms-modal" @hide="dismissVerification()" :visible="showValidation" center hide-header hide-footer>
              <template v-slot:default="{ hide }">
                <div class="mx-5 mt-5 mb-4 text-center" v-if="validationStep == 'intro'">
                  <div class="mb-3">
                    <h1 class="font-bigger-4 font-weight-bold">Verify your phone number</h1>
                  </div>
                  <br />
                  <p class="mb-4 font-subheader text-left">We'd like to verify your phone number to get your contribution matched. Phone number verification is optional.</p>
                  <br />
                  <p class="mb-4 font-subheader text-left">Verifying increases your trust level and impact of your contributions. You can still contribute to grants without
                  verifying your phone number, but your contribution impact will be reduced.</p>
                  <br />
                  <p class="mb-4 font-subheader text-left">Gitcoin does NOT store your phone number.</p>
                  <br />
                  <p class="mb-4 font-subheader text-left">read more about <a target="_blank" rel="noopener noreferrer" class="gc-text-blue font-smaller-1"
                    href="https://twitter.com/owocki/status/1271088915982675974">why we are asking for your phone number</a> or how Gitcoin <a target="_blank" rel="noopener noreferrer" class="gc-text-blue font-smaller-1"
                      href="https://twitter.com/owocki/status/1271088915982675974">preserves your privacy.</a></p>
                  <b-button @click="validationStep='requestVerification'" class="btn-gc-blue mb-2" size="lg">Verify
                  Phone Number</b-button>
                  <div class="mb-1 font-subheader text-center">
                    <a id="verify_offline" href="#">
                    <br />
                    Verify Offline or</a>  <a href="#" @click="dismissVerification()" variant="link">Skip</a>
                    <div id='verify_offline_target' style="display:none">
                      <strong>Verify Offline</strong>
                      <br />
                      <a href="mailto:kyc@gitcoin.co">Email Gitcoin</a> or <a href="https://keybase.io/gitcoin_verify">Message Gitcoin on Keybase</a>, and we will verify your information within 1-2 business days.
                      <br />
                      IMPORTANT: Be sure to include (1) your gitcoin username (2) proof of ownership of a SMS number.
                    </div>
                  </div>
                </div>
                <div class="mx-5 my-5 text-center" v-if="validationStep == 'requestVerification'">
                  <div class="mb-3">
                    <h1 class="font-bigger-4 font-weight-bold">Verify your phone number</h1>
                  </div>
                  <p class="mb-5 font-subheader">We will send you a verification code.</p>
                  <vue-tel-input ref="tel-input" :validCharactersOnly="true" @validate="isValidNumber" v-model="phone"
                    :enabledCountryCode="true" :autofocus="true" :required="true" mode="international"
                    inputClasses="form-control" placeholder="+1 8827378273"
                    :inputOptions="{showDialCode: true}"
                  ></vue-tel-input>
                  <div v-if="timeInterval > timePassed">
                    <span class="label-warning">Wait [[ timeInterval - timePassed ]] second before request another
                      code</span>
                  </div>
                  <div v-if="errorMessage">
                    <span class="label-warning">[[ errorMessage ]]</span>
                  </div>
                  <b-button @click="requestVerification()" class="btn-gc-blue mt-5 mb-2" size="lg">Send verification
                    code</b-button>
                  <br />
                  <b-button @click="hide()" variant="link">Cancel</b-button>
                </div>
                <div class="mx-5 my-5 text-center" v-if="validationStep == 'verifyNumber'">
                  <div class="mb-3">
                    <h1 class="font-bigger-4 font-weight-bold">Verify your phone number</h1>
                  </div>
                  <p class="mb-5 font-subheader">Enter the verification code sent to your number.</p>

                  <input class="form-control" type="number" required v-model="code">
                  <div v-if="timeInterval > timePassed">
                    <span class="label-warning">Wait [[ timeInterval - timePassed ]] second before request another
                      code</span>
                  </div>
                  <div v-if="errorMessage">
                    <span class="label-warning">[[ errorMessage ]]</span>
                  </div>
                  <b-button @click="validateCode()" class="btn-gc-blue mt-5" size="lg">Submit</b-button>
                  <br />
                  <b-button @click="startVerification()" variant="link">Change number</b-button>
                  <b-button @click="resendCode()" variant="link">Resend Code</b-button>
                    <b-button @click="resendCode('email')" variant="link" v-if="display_email_option">Send email</b-button>
                </div>
              </template>
            </b-modal>`,
  methods: {
    dismissVerification() {
      localStorage.setItem('dismiss-sms-validation', true);
      this.$emit('modal-dismissed');
    },
    // VALIDATE
    validateCode() {
      const vm = this;

      if (vm.code) {
        const verificationRequest = fetchData('/sms/validate/', 'POST', {
          code: vm.code,
          phone: vm.phone
        }, {'X-CSRFToken': vm.csrf});

        $.when(verificationRequest).then(response => {
          vm.verificationEnabled = false;
          vm.verified = true;
          vm.validationStep = 'verifyNumber';
          vm.$emit('modal-dismissed');
          _alert('You have been verified. <a href="" style="color: white; text-decoration: underline;">Refresh Page</a>.', 'success');
        }).catch((e) => {
          vm.errorMessage = e.responseJSON.msg;
        });
      }
    },
    startVerification() {
      this.phone = '';
      this.validationStep = 'requestVerification';
      this.validNumber = false;
      this.errorMessage = '';
      this.code = '';
      this.timePassed = 0;
      this.timeInterval = 0;
      this.display_email_option = false;
    },
    countdown() {
      const vm = this;

      if (!vm.countDownActive) {
        vm.countDownActive = true;

        setInterval(() => {
          vm.timePassed += 1;
        }, 1000);
      }
    },
    resendCode(delivery_method) {
      const e164 = this.phone.replace(/\s/g, '');
      const vm = this;

      vm.errorMessage = '';

      if (vm.validNumber) {
        const verificationRequest = fetchData('/sms/request', 'POST', {
          phone: e164,
          delivery_method: delivery_method || 'sms'
        }, {'X-CSRFToken': vm.csrf});

        vm.errorMessage = '';

        $.when(verificationRequest).then(response => {
          // set the cooldown time to one minute
          this.timePassed = 0;
          this.timeInterval = 60;
          this.countdown();
          this.display_email_option = response.allow_email;
        }).catch((e) => {
          vm.errorMessage = e.responseJSON.msg;
        });
      }
    },
    // REQUEST VERIFICATION
    requestVerification(event) {
      const e164 = this.phone.replace(/\s/g, '');
      const vm = this;

      if (vm.validNumber) {
        const verificationRequest = fetchData('/sms/request', 'POST', {
          phone: e164
        }, {'X-CSRFToken': vm.csrf});

        vm.errorMessage = '';

        $.when(verificationRequest).then(response => {
          vm.validationStep = 'verifyNumber';
          this.timePassed = 0;
          this.timeInterval = 60;
          this.countdown();
          this.display_email_option = response.allow_email;
        }).catch((e) => {
          vm.errorMessage = e.responseJSON.msg;
        });
      }
    },
    isValidNumber(validation) {
      console.log(validation);
      this.validNumber = validation.isValid;
    }
  }
});

Vue.component('twitter-verify-modal', {
  delimiters: [ '[[', ']]' ],
  data: function() {
    return {
      validationStep: 'send-tweet',
      tweetText: '',
      twitterHandle: '',
      validationError: ''
    };
  },
  props: {
    showValidation: {
      type: Boolean,
      required: false,
      'default': false
    }
  },
  computed: {
    encodedTweetText: function() {
      return encodeURIComponent(this.tweetText);
    },
    tweetIntentURL: function() {
      return `https://twitter.com/intent/tweet?text=${this.encodedTweetText}`;
    }
  },
  mounted: function() {
    this.tweetText = verifyTweetText; // Global from tab_trust.html <script> tag
  },
  template: `<b-modal id="twitter-modal" @hide="dismissVerification()" :visible="showValidation" center hide-header hide-footer>
                <template v-slot:default="{ hide }">
                  <div class="mx-5 mt-5 mb-4 text-center">
                    <div class="mb-3">
                      <h1 class="font-bigger-4 font-weight-bold">Verify your Twitter account</h1>
                    </div>
                    <div v-if="validationStep === 'send-tweet'">
                      <p class="mb-4 font-subheader text-left">
                        We want to verify your Twitter account. To do so, you must first send a standardized
                        Tweet from your account, then we'll validate it's there.
                      </p>
                      <p class="mb-4 font-subheader text-left">
                        The Tweet should say:
                      </p>
                      <p class="mb-4 font-subheader text-left">
                        <em>[[tweetText]]</em>
                      </p>
                      <div class="mt-2 mb-2">
                        <a :href="tweetIntentURL" @click="clickedSendTweet" role="button" style="font-size: 1.3em" class="button button--primary mb-2" target="_blank">
                          Send Tweet
                        </a>
                      </div>
                      <a href="" @click="clickedAlreadySent">
                        I have already Tweeted this
                      </a>
                    </div>
                    <div v-if="validationStep === 'validate-tweet' || validationStep == 'perform-validation'">
                      <p class="mb-4">
                        Now we'll validate that you've sent the tweet. Enter your Twitter handle and press validate.
                      </p>
                      <div class="input-group">
                        <div class="input-group-prepend">
                          <span class="input-group-text form-control" id="basic-addon1">@</span>
                        </div>
                        <input type="text" class="form-control" placeholder="handle" aria-label="handle" aria-describedby="basic-addon1" required maxlength="15" v-model="twitterHandle">
                      </div>
                      <div v-if="validationError !== ''" style="color: red">
                        <small>[[validationError]]</small>
                      </div>
                      <b-button @click="clickedValidate" :disabled="validationStep === 'perform-validation'" class="btn-gc-blue mt-3 mb-2" size="lg">
                        <b-spinner v-if="validationStep === 'perform-validation'" type="grow"></b-spinner>
                        Validate
                      </b-button>
                      <br />
                      <a href="" v-if="validationError !== ''" @click="clickedGoBack">
                        Go Back
                      </a>
                    </div>
                    <div v-if="validationStep === 'validation-complete'">
                      Your Twitter verification was successful. Thank you for helping make Gitcoin more sybil resistant!
                      <a href="" class="btn btn-gc-blue px-5 mt-3 mb-2 mx-2" role="button" style="font-size: 1.3em">Done</a>
                    </div>
                  </div>
                </template>
            </b-modal>`,
  methods: {
    dismissVerification() {
      this.$emit('modal-dismissed');
    },
    clickedSendTweet(event) {
      this.validationStep = 'validate-tweet';
    },
    clickedAlreadySent(event) {
      event.preventDefault();
      this.validationStep = 'validate-tweet';
    },
    clickedGoBack(event) {
      event.preventDefault();
      this.validationStep = 'send-tweet';
      this.validationError = '';
    },
    clickedValidate(event) {
      event.preventDefault();

      this.twitterHandle = this.twitterHandle.trim();

      // Strip leading @ if user includes it
      if (this.twitterHandle.startsWith('@')) {
        this.twitterHandle = this.twitterHandle.split('@')[1];
      }

      // Validate handle is 15 word characters
      const isValidHandle = null !== this.twitterHandle.match(/^(\w){1,15}$/);

      if (!isValidHandle) {
        this.validationError = 'Please enter a valid Twitter handle';
        return;
      }

      // Reset after a prior error
      this.validationError = '';

      this.validationStep = 'perform-validation';

      this.verifyTwitter();
    },
    verifyTwitter() {
      const csrfmiddlewaretoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
      const payload = JSON.stringify({
        'twitter_handle': this.twitterHandle
      });
      const headers = {'X-CSRFToken': csrfmiddlewaretoken};

      const verificationRequest = fetchData(`/api/v0.1/profile/${trustHandle}/verify_user_twitter`, 'POST', payload, headers);

      $.when(verificationRequest).then(response => {
        if (response.ok) {
          this.validationStep = 'validation-complete';
        } else {
          this.validationError = response.msg;
          this.validationStep = 'validate-tweet';
        }

      }).catch((_error) => {
        this.validationError = 'There was an error; please try again later';
        this.validationStep = 'validate-tweet';
      });
    }
  }
});

Vue.component('poap-verify-modal', {
  delimiters: [ '[[', ']]' ],
  data: function() {
    return {
      hideTemporarily: false,
      validationStep: 'validate-address',
      ethAddress: '',
      signature: '',
      validationError: ''
    };
  },
  props: {
    showValidation: {
      type: Boolean,
      required: false,
      'default': false
    }
  },
  template: `<b-modal id="poap-modal" @hide="dismissVerification()" :visible="showValidation && !hideTemporarily" center hide-header hide-footer>
                <template v-slot:default="{ hide }">
                  <div class="mx-5 mt-5 mb-4 text-center">
                    <div class="mb-3">
                      <img src="/static/v2/images/project_logos/poap.svg" alt="POAP Logo" width="100">
                      <h1 class="font-bigger-4 font-weight-bold mt-2">Verify your POAP badges</h1>
                    </div>
                    <div v-if="validationStep === 'validate-address'">
                      <p class="mb-4 font-subheader text-left">
                        POAP is a software system that allows humans to collect badges (in the form of non fungible tokens) every time they participate in an activity,
                        whether in person or remotely. <a href="https://www.poap.xyz/#faqs" target="_blank">Learn more.</a>
                      </p>
                      <p class="mb-4 font-subheader text-left">
                        We want to verify your POAP badges. To do so, you must first connect with your preferred web3 account.
                        Then, we'll validate your account holds at least one POAP badge, and that it's been there for at least 15 days.
                      </p>

                      <div class="mt-2 mb-2">
                        <a href="" @click="clickedPullEthAddress" role="button" style="font-size: 1.3em" class="button button--primary mb-2" target="_blank">
                          Pull from Wallet
                        </a>
                      </div>
                    </div>
                    <div v-if="validationStep === 'validate-poap' || validationStep == 'perform-validation'">
                      <p class="mb-4">
                        We'll check for POAP badges held by the following account.
                      </p>
                      <div class="input-group">
                        <input type="text" readonly class="form-control" placeholder="eth-address" aria-label="handle" aria-describedby="basic-addon1" required maxlength="255" v-model="ethAddress">
                      </div>
                      <div v-if="validationError !== ''" style="color: red">
                        <small>[[validationError]]</small>
                      </div>
                      <b-button @click="clickedValidate" :disabled="validationStep === 'perform-validation'" class="btn-gc-blue mt-3 mb-2" size="lg">
                        <b-spinner v-if="validationStep === 'perform-validation'" type="grow"></b-spinner>
                        Validate
                      </b-button>
                      <br />
                        <a href="" @click="clickedChangeWallet" :disabled="validationStep === 'perform-validation'">
                          Change Wallet
                        </a>
                      <br />
                      <a href="" v-if="validationError !== ''" @click="clickedGoBack">
                        Go Back
                      </a>
                    </div>
                    <div v-if="validationStep === 'validation-complete'">
                      Your POAP verification was successful. Thank you for helping make Gitcoin more sybil resistant!
                      <a href="" class="btn btn-gc-blue px-5 mt-3 mb-2 mx-2" role="button" style="font-size: 1.3em">Done</a>
                    </div>
                  </div>
                </template>
            </b-modal>`,
  methods: {
    dismissVerification() {
      // If we're only hiding the modal to allow wallet selection, don't emit this event, which
      // would prevent it from popping up again after the user completes their selection.
      if (!this.hideTemporarily) {
        this.$emit('modal-dismissed');
      }
    },
    clickedGoBack(event) {
      event.preventDefault();
      this.validationStep = 'validate-address';
      this.ethAddress = '';
      this.validationError = '';
    },
    getEthAddress() {
      const accounts = web3.eth.getAccounts();

      $.when(accounts).then((result) => {
        const ethAddress = result[0];

        this.ethAddress = ethAddress;
        this.validationStep = 'validate-poap';
        // this.showValidation = true;
        this.hideTemporarily = false;
      }).catch((_error) => {
        this.validationError = 'Error getting ethereum accounts';
        this.validationStep = 'validate-address';
        // this.showValidation = true;
        this.hideTemporarily = false;
      });

    },
    generateSignature() {
      // Create a signature using the provided web3 account
      web3.eth.personal.sign('verify_poap_badges', this.ethAddress)
        .then(signature => {
          this.signature = signature;
          this.verifyPOAP();
        });
    },
    connectWeb3Wallet() {
      // this.showValidation = false;
      this.hideTemporarily = true;
      onConnect().then((result) => {
        this.getEthAddress();
      }).catch((_error) => {
        this.validationError = 'Error connecting ethereum accounts';
        this.validationStep = 'validate-address';
        // this.showValidation = true;
        this.hideTemporarily = false;
      });
    },
    clickedPullEthAddress(event) {
      // Prompt web3 login if not connected
      event.preventDefault();
      if (!provider) {
        this.connectWeb3Wallet();
      } else {
        this.getEthAddress();
      }
    },
    clickedChangeWallet(event) {
      event.preventDefault();
      this.validationError = '';
      this.connectWeb3Wallet();
    },
    clickedValidate(event) {
      event.preventDefault();
      this.validationError = '';
      this.validationStep = 'perform-validation';
      this.generateSignature();
    },
    verifyPOAP() {
      const csrfmiddlewaretoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
      const payload = JSON.stringify({
        'eth_address': this.ethAddress,
        'signature': this.signature
      });
      const headers = {'X-CSRFToken': csrfmiddlewaretoken};

      const verificationRequest = fetchData(`/api/v0.1/profile/${trustHandle}/verify_user_poap`, 'POST', payload, headers);

      $.when(verificationRequest).then(response => {
        if (response.ok) {
          this.validationStep = 'validation-complete';
        } else {
          this.validationError = response.msg;
          this.validationStep = 'validate-poap';
        }

      }).catch((_error) => {
        console.log(_error);
        this.validationError = 'There was an error; please try again later';
        this.validationStep = 'validate-poap';
      });
    }
  }
});

Vue.component('brightid-verify-modal', {
  delimiters: [ '[[', ']]' ],
  data: function() {
    return {
      calls: []
    };
  },
  props: {
    showValidation: {
      type: Boolean,
      required: false,
      'default': false
    },
    validationStep: {
      type: String,
      required: true
    },
    brightidUuid: {
      type: String,
      required: true
    }
  },
  computed: {
    brightIdLink() {
      return `https://app.brightid.org/link-verification/http:%2f%2fnode.brightid.org/Gitcoin/${this.brightidUuid}`;
    },
    brightIdAppLink() {
      return `brightid://link-verification/http:%2f%2fnode.brightid.org/Gitcoin/${this.brightidUuid}`;
    }
  },
  mounted() {
    if (calendarData) {
      this.calls = calendarData;
    }
  },
  template: `<b-modal id="brightid-modal" @hide="dismissVerification()" :visible="showValidation" center hide-header hide-footer>
              <template v-slot:default="{ hide }">
                <div class="modal-content px-2 py-2">
                  <div class="col-12">
                    <button @click="dismissVerification()" type="button" class="close" data-dismiss="modal" aria-label="Close">
                      <span aria-hidden="true">&times;</span>
                    </button>
                  </div>
                  <template v-if="validationStep === 'connect-brightid'">
                    <div class="col-12 pt-2 pb-2 text-center">
                      <img src="/static/v2/images/project_logos/brightid.png" alt="BrightID Logo" width="100">
                      <h2 class="font-title mt-2">Connect With BrightID</h2>
                    </div>
                    <div class="col-12 pt-2">
                      <p>
                        BrightID is a digital identity solution that ensures accounts in any application are created by real humans; each user is unique and only has one account.
                        <a href="https://www.brightid.org/" target="_blank">Learn More</a>.
                      </p>
                      <p>
                        To increase your Trust Bonus using BrightID, you must first get connected. Follow these steps:
                      </p>
                      <p>
                        <strong>Step 1</strong>: Download the BrightID App on your mobile device<br />
                        <a href="https://apps.apple.com/us/app/brightid/id1428946820">
                          <img src="/static/v2/images/app_stores/apple_app_store.svg" width="100">
                        </a>
                        <a href="https://play.google.com/store/apps/details?id=org.brightid">
                          <img src="/static/v2/images/app_stores/google_play_store.png" width="125">
                        </a>
                      </p>
                      <p>
                        <strong>Step 2</strong>: Connect BrightID to Gitcoin by scanning this QR code
                        from the BrightID app, or <a :href="brightIdLink">clicking here</a> from your mobile device.
                        <div style="display: flex; justify-content: center; text-align: center;">
                          <qrcode :string="brightIdAppLink" :size="175"></qrcode>
                        </div>
                      </p>
                      <div class="col-12 my-4 text-center">
                        <a href="" class="btn btn-gc-blue px-5 mb-2 mx-2">Done Connecting</a>
                      </div>
                    </div>
                  </template>
                  <template v-else-if="validationStep === 'verify-brightid'">
                    <div class="col-12 pt-2 pb-2 text-center">
                      <img src="/static/v2/images/project_logos/brightid.png" alt="BrightID Logo" width="100">
                      <h2 class="font-title mt-2">Verify Your BrightID</h2>
                    </div>
                    <div class="col-12 pt-2">
                      <p>
                        BrightID is a digital identity solution that ensures accounts in any application are created by real humans; each user is unique and only has one account.
                        <a href="https://www.brightid.org/" target="_blank">Learn More</a>.
                      </p>
                      <p>
                        Now that you've connected your BrightID, you need to get verified by connecting with other real humans.
                      </p>
                      <p>
                        <strong>Join a Gitcoin + BrightID Verification Party</strong><br />
                        <small class="text-muted">
                          You can learn more about how BrightID works and make connections that will help you get verified on the verifications parties.
                          Register for one of the events.
                        </small>
                        <template v-for="call in calls">
                          <div class="row mb-3">
                            <div class="col-md-8">
                              <strong class="d-block">[[call.when]]</strong>
                              <div class="font-caption">
                                <template v-for="date in call.dates">
                                  At <span>[[formatDate(date.timeStart)]]</span> - <span>[[formatDate(date.timeEnd)]]</span><br />
                                </template>
                              </div>
                            </div>
                            <div class="col-md-4 my-auto">
                              <a :href="call.link" target="_blank" class="btn btn-sm btn-block btn-gc-blue px-4 font-caption font-weight-bold">Register <br> on [[call.platform]]</a>
                            </div>
                          </div>
                        </template>
                      </p>
                    </div>
                  </template>
                </div>
              </template>
            </b-modal>`,
  methods: {
    dismissVerification() {
      this.$emit('modal-dismissed');
    },
    formatDate(date) {
      let options = {hour: 'numeric', minute: 'numeric', dayPeriod: 'short'};

      return new Intl.DateTimeFormat('en-US', options).format(new Date(date));
    }
  }
});

Vue.component('active-trust-manager', {
  delimiters: [ '[[', ']]' ],
  data() {
    return {
      visibleModal: 'none'
    };
  },
  methods: {
    showModal(modalName) {
      this.visibleModal = modalName;
    },
    hideModal() {
      this.visibleModal = 'none';
    }
  }
});

Vue.component('active-trust-row-template', {
  delimiters: [ '[[', ']]' ],
  data() {
    return {};
  },
  props: {
    iconType: {
      type: String, // 'image' or 'markup'
      required: false,
      'default': 'markup'
    },
    iconPath: {
      // path to image file if iconType is 'image'
      type: String,
      required: false
    },
    title: {
      type: String,
      required: true
    },
    matchPercent: {
      type: Number,
      required: true
    },
    isVerified: {
      type: Boolean,
      required: true
    },
    buttonText: {
      type: String,
      required: false,
      'default': 'Verify'
    }
  },
  methods: {
    didClick(event) {
      event.preventDefault();
      this.$emit('verify-button-pressed');
    },
    hasVerifySlot() {
      return !!this.$slots.verify;
    }
  },
  template: `
      <div class="row mb-4">
        <div class="col-12 col-md-1 mx-auto text-center">
          <div v-if="iconType === 'markup'">
            <slot name="icon"></slot>
          </div>
          <div v-if="iconType === 'image'">
            <img :src="[[iconPath]]" alt="logo" class="img-fluid">
          </div>
        </div>
        <div class="col-12 col-md-7 mb-3 mb-md-0">
          <div class="font-weight-bold">
            [[title]]
          </div>
          <div>
            <slot name="description"></slot>
          </div>
        </div>
        <div class="col-6 col-md-2 text-center">
          <div class="font-weight-bold">
            +[[matchPercent]]%
          </div>
          <div style="color:grey">
            <small>Grants CLR Match</small>
          </div>
        </div>
        <div class="col-6 col-md-2">
          <template v-if="hasVerifySlot()">
            <slot name="verify"></slot>
          </template>
          <template v-else>
            <template v-if="isVerified === true">
              <span style="color:limegreen"><i class="fas fa-check"></i> Verified</span>
            </template>
            <template v-else>
              <a @click="didClick" href="" role="button" class="button button--primary text-nowrap">[[buttonText]]</a>
            </template>
          </template>
        </div>
      </div>
  `
});

if (document.getElementById('gc-trust-manager-app')) {

  const trustManagerApp = new Vue({
    delimiters: [ '[[', ']]' ],
    el: '#gc-trust-manager-app',
    data: { }
  });
}

$(document).ready(function() {
  $(document).on('keyup', 'input[name=telephone]', function(e) {
    var number = $(this).val();

    if (number[0] != '+') {
      number = '+' + number;
      $(this).val(number);
    }
  });

  $(document).on('click', '#verify_offline', function(e) {
    $(this).remove();
    $('#verify_offline_target').css('display', 'block');
  });
});
