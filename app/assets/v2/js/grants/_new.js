Vue.component('v-select', VueSelect.VueSelect);
Vue.use(VueQuillEditor);

Vue.mixin({
  methods: {
    showQuickStart: function() {

      fetch('/grants/quickstart')
        .then(function(response) {
          return response.text();
        }).then(function(html) {
          let parser = new DOMParser();
          let doc = parser.parseFromString(html, 'text/html');

          doc.querySelector('.btn-closeguide').dataset.dismiss = 'modal';

          let docArticle = doc.querySelector('.content').innerHTML;
          const content = $.parseHTML(
            `<div id="gitcoin_updates" class="modal fade" tabindex="-1" role="dialog" aria-hidden="true">
              <div class="modal-dialog modal-xl" style="max-width:95%">
                <div class="modal-content px-4 py-3">
                  <div class="col-12">
                    <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                      <span aria-hidden="true">&times;</span>
                    </button>
                  </div>
                  ${docArticle}
                  <div class="col-12 my-4 d-flex justify-content-around">
                    <button type="button" class="btn btn-gc-blue" data-dismiss="modal" aria-label="Close">Close</button>
                  </div>
                </div>
              </div>
            </div>`);

          $(content).appendTo('body');
          $('#gitcoin_updates').bootstrapModal('show');
          setupTabs('#grant-quickstart-tabs');
        });

      $(document, '#gitcoin_updates').on('hidden.bs.modal', function(e) {
        $('#gitcoin_updates').remove();
        $('#gitcoin_updates').bootstrapModal('dispose');
      });
    },
    userSearch(search, loading) {
      let vm = this;

      if (search.length < 3) {
        return;
      }
      loading(true);
      vm.getUser(loading, search);

    },
    getUser: async function(loading, search, selected) {
      let vm = this;
      let myHeaders = new Headers();
      let url = `/api/v0.1/users_search/?token=${currentProfile.githubToken}&term=${escape(search)}&suppress_non_gitcoiners=true`;

      myHeaders.append('X-Requested-With', 'XMLHttpRequest');
      return new Promise(resolve => {

        fetch(url, {
          credentials: 'include',
          headers: myHeaders
        }).then(res => {
          res.json().then(json => {
            vm.$set(vm, 'usersOptions', json);
            if (selected) {
              // TODO: BUG -> Make append
              vm.$set(vm.form, 'team_members', vm.usersOptions[0].text);
            }
            resolve();
          });
          if (loading) {
            loading(false);
          }
        });
      });
    },
    checkForm: function(e) {
      let vm = this;

      vm.submitted = true;
      vm.errors = {};
      if (!vm.form.title.length) {
        vm.$set(vm.errors, 'title', 'Please enter the title');
      }
      if (!vm.form.reference_url.length) {
        vm.$set(vm.errors, 'reference_url', 'Please enter link to the project');
      }
      if (!vm.form.twitter_handle_1.length) {
        vm.$set(vm.errors, 'twitter_handle_1', 'Please enter twitter handle of your project');
      }
      if (!vm.chainId) {
        vm.$set(vm.errors, 'chainId', 'Please select an option');
      } else if (vm.chainId == 'eth' && !vm.form.eth_payout_address) {
        vm.$set(vm.errors, 'eth_payout_address', 'Please enter ETH address');
      } else if (
        vm.chainId == 'zcash' &&
            (!vm.form.zcash_payout_address || !vm.form.zcash_payout_address.toLowerCase().startsWith('t'))
      ) {
        vm.$set(vm.errors, 'zcash_payout_address', 'Please enter transparent ZCash address');
      }
      if (!vm.form.grant_type) {
        vm.$set(vm.errors, 'grant_type', 'Please select the grant category');
      }
      if (!vm.form.grant_categories.length > 0) {
        vm.$set(vm.errors, 'grant_categories', 'Please one or more grant subcategory');
      }
      if (vm.form.description_rich.length < 10) {
        vm.$set(vm.errors, 'description', 'Please enter description for the grant');
      }

      if (Object.keys(vm.errors).length) {
        return false; // there are errors the user must correct
      }
      vm.submitted = false;
      return true; // no errors, continue to create grant
    },
    submitForm: async function(event) {
      event.preventDefault();
      let vm = this;
      let form = vm.form;

      // Exit if form is not valid
      if (!vm.checkForm(event))
        return;

      const params = {
        'title': form.title,
        'reference_url': form.reference_url,
        'logo': vm.logo,
        'description': vm.$refs.quillEditorDesc.quill.getText(),
        'description_rich': JSON.stringify(vm.$refs.quillEditorDesc.quill.getContents()),
        'team_members[]': form.team_members,
        'handle1': form.twitter_handle_1,
        'handle2': form.twitter_handle_2,
        'github_project_url': form.github_project_url,
        'eth_payout_address': form.eth_payout_address,
        'zcash_payout_address': form.zcash_payout_address,
        'grant_type': form.grant_type,
        'categories[]': form.grant_categories,
        'network': form.network
        // logoPreview
        // admin_address
        // contract_owner_address
        // token_address
        // token_symbol
        // contract_version
        // transaction_hash
        // contract_address
        // transaction_hash
      };

      console.log(params);
      vm.submitted = true;
      vm.submitGrant(params);

    },
    submitGrant(data) {
      let vm = this;

      if (typeof ga !== 'undefined') {
        ga('send', 'event', 'Create Grant', 'click', 'Grant Creator');
      }

      const headers = {
        'X-CSRFToken': $("input[name='csrfmiddlewaretoken']").val()
      };

      const apiUrlGrant = '/grants/new';

      $.ajax({
        type: 'post',
        url: apiUrlGrant,
        processData: false,
        contentType: false,
        data: getFormData(data),
        headers: headers,
        success: response => {
          if (response.status == 200) {
            window.location = response.url;
          } else {
            vm.submitted = false;
            _alert('Unable to create grant. Please try again', 'error');
            console.error(`error: grant creation failed with status: ${response.status} and message: ${response.message}`);
          }
        },
        error: err => {
          vm.submitted = false;
          _alert('Unable to create grant. Please try again', 'error');
          console.error(`error: grant creation failed with msg ${err}`);
        }
      });
    },
    type_to_category_mapping: function() {
      let vm = this;

      let grant_type = this.grant_types.filter(grant_type => grant_type.name == vm.form.grant_type);

      return grant_type[0].categories;
    }
  },
  watch: {
    deep: true,
    teamMembers: {
      handler(newVal, oldVal) {
        let team_members_id;

        team_members_id = newVal.reduce((oldItem, newItem)=> {
          oldItem.push(newItem.id);
          return oldItem;
        }, []);
        return this.$set(this.form, 'team_members', team_members_id);

      }

    },
    form: {
      deep: true,
      handler(newVal, oldVal) {
        if (this.dirty && this.submitted) {
          this.checkForm();
        }
        this.dirty = true;
      }
    },
    logo: {
      deep: true,
      handler(newVal, oldVal) {
        let vm = this;

        if (checkFileSize(this.logo, 4000000) === false) {
          _alert(`Grant Image should not exceed ${(4000000 / 1024 / 1024).toFixed(2)} MB`, 'error');
        } else {
          let reader = new FileReader();

          reader.onload = function(e) {
            vm.logoPreview = e.target.result;
            $('#preview').css('width', '100%');
            $('#js-drop span').hide();
            $('#js-drop input').css('visible', 'invisible');
            $('#js-drop').css('padding', 0);
          };
          reader.readAsDataURL(vm.logo);
        }
      }
    }
  }
});

if (document.getElementById('gc-new-grant')) {
  appFormBounty = new Vue({
    delimiters: [ '[[', ']]' ],
    el: '#gc-new-grant',
    components: {
      'vue-select': 'vue-select'
    },
    data() {
      return {
        chainId: '',
        grant_types: document.grant_types,
        usersOptions: [],
        network: 'mainnet',
        logo: null,
        logoPreview: null,
        teamMembers: [],
        submitted: false,
        errors: {},
        form: {
          title: '',
          reference_url: '',
          description_rich: '',
          team_members: [],
          twitter_handle_1: '',
          twitter_handle_2: '',
          github_project_url: '',
          eth_payout_address: '',
          zcash_payout_address: '',
          grant_type: '',
          grant_categories: [],
          network: 'mainnet'
        },
        editorOptionPrio: {
          modules: {
            toolbar: [
              [ 'bold', 'italic', 'underline' ],
              [{ 'align': [] }],
              [{ 'list': 'ordered'}, { 'list': 'bullet' }],
              [ 'link', 'code-block' ],
              ['clean']
            ]
          },
          theme: 'snow',
          placeholder: 'Give a detailed desciription about your Grant'
        }
      };
    }
  });
}
