const express = require("express");
const request = require("request");
const cheerio = require("cheerio");

const app = express();

app.get("/", (req, res) => {
  const { first, second } = req.query;

  if (!first || !second) {
    return res.json({ error: "Enter ?first=DL8C and ?second=1234" });
  }

  let data = {
    'javax.faces.partial.ajax':'true',
    'javax.faces.source': 'form_rcdl:j_idt32',
    'javax.faces.partial.execute':'@all',
    'javax.faces.partial.render': 'form_rcdl:pnl_show form_rcdl:pg_show form_rcdl:rcdl_pnl',
    'form_rcdl:j_idt32':'form_rcdl:j_idt32',
    'form_rcdl':'form_rcdl',
    'form_rcdl:tf_reg_no1': first,
    'form_rcdl:tf_reg_no2': second
  };

  request.post({url: 'https://parivahan.gov.in/rcdlstatus/'}, (err, httpResponse, html) => {
    if (err) return res.json({ error: "Initial request failed" });

    const $ = cheerio.load(html);
    let token = $('input[name="javax.faces.ViewState"]').val();
    let cookies = httpResponse.headers['set-cookie'];
    data['javax.faces.ViewState'] = token;

    request.post({
      url: 'https://parivahan.gov.in/rcdlstatus/',
      form: data,
      headers: {Cookie: cookies}
    }, (err2, httpResponse2, html2) => {

      if (err2) return res.json({ error: "Second request failed" });

      let $$ = cheerio.load(html2);
      let output = {};

      $$('table td').each(function() {
        let k = $$(this).text().trim();
        let v = $$(this).next().text().trim();
        if (k && v) output[k] = v;
      });

      res.json(output);
    });
  });
});

app.listen(process.env.PORT || 8080, () => console.log("RC API Running"));
