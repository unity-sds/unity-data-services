"use strict";(self["webpackChunk_radiantearth_stac_browser"]=self["webpackChunk_radiantearth_stac_browser"]||[]).push([[8980],{68980:function(t,e,a){a.r(e),a.d(e,{default:function(){return p}});var i=function(){var t=this,e=t._self._c;return e("div",{staticClass:"auth"},[e("b-form",{on:{submit:function(e){return e.stopPropagation(),e.preventDefault(),t.submit.apply(null,arguments)},reset:t.reset}},[e("b-card",{attrs:{"no-body":"",header:t.$t("authentication.title")}},[e("b-card-body",[e("p",[t._v(t._s(t.$t("authentication.description")))]),t.description?e("Description",{attrs:{description:t.description}}):t._e(),e("b-form-input",{staticClass:"mb-2 mt-2",attrs:{type:"password",autofocus:"",required:t.required},model:{value:t.token,callback:function(e){t.token="string"===typeof e?e.trim():e},expression:"token"}})],1),e("b-card-footer",[e("b-button",{attrs:{type:"submit",variant:"primary"}},[t._v(t._s(t.$t("submit")))]),e("b-button",{staticClass:"ml-3",attrs:{type:"reset",variant:"danger"}},[t._v(t._s(t.$t("cancel")))])],1)],1)],1)],1)},r=[],n=a(44093),s=a(96296),o=a(46584),u=a(48416),c={name:"Authentication",components:{BForm:s.E,BFormInput:o.U,Description:n["default"]},data(){return{token:"",required:!0}},computed:{...(0,u.ys)(["authConfig","authData"]),description(){return this.authConfig.description?this.authConfig.description:this.$t("authConfig.description")}},created(){this.authData&&(this.token=this.authData,this.required=!1)},methods:{reset(){this.$store.commit("requestAuth",null)},async submit(){await this.$store.dispatch("setAuth",this.token),await this.$store.dispatch("retryAfterAuth"),this.$store.commit("requestAuth",null)}}},d=c,l=a(82528),h=(0,l.c)(d,i,r,!1,null,null,null),p=h.exports},96296:function(t,e,a){a.d(e,{E:function(){return c}});var i=a(77548),r=a(76516),n=a(99628),s=a(95756),o=a(97637),u=(0,o.a8)({id:(0,o.K2)(s.nV),inline:(0,o.K2)(s.aM,!1),novalidate:(0,o.K2)(s.aM,!1),validated:(0,o.K2)(s.aM,!1)},n.U$),c=(0,i.SU)({name:n.U$,functional:!0,props:u,render:function(t,e){var a=e.props,i=e.data,n=e.children;return t("form",(0,r.k)(i,{class:{"form-inline":a.inline,"was-validated":a.validated},attrs:{id:a.id,novalidate:a.novalidate}}),n)}})}}]);
//# sourceMappingURL=8980.7852a14e.js.map