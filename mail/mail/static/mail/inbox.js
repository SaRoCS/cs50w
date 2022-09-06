document.addEventListener('DOMContentLoaded', function() {

  // Use buttons to toggle between views
  document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
  document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
  document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
  document.querySelector('#compose').addEventListener('click', () => compose_email(reply=false, id=undefined));

  // By default, load the inbox
  load_mailbox('inbox');
});

function compose_email(reply, id) {

  // Show compose view and hide other views
  document.querySelector("#email-view").style.display = 'none';
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';

  

  if (reply === false) {
    // Clear out composition fields
    document.querySelector('#compose-recipients').value = '';
    document.querySelector('#compose-subject').value = '';
    document.querySelector('#compose-body').value = '';
  } else {

    fetch(`/emails/${id}`)
    .then(response => response.json())
    .then(email => {
      console.log(email);
      document.querySelector('#compose-recipients').value = email.sender;
      let s = email.subject;
      let sub = s.slice(0,3);
      if (sub == "Re:"){
        document.querySelector('#compose-subject').value = email.subject;
        const reply = email.body.split("\n");
        let message = '';
        const len = reply.length - 1;
        reply.forEach(element => {
          if (reply[len] === element){
            message += `On ${email.timestamp} ${email.sender} replied: ${element}`;
          }else{
            message += `${element} \n`;
          }
        });
        document.querySelector("#compose-body").value = message;
      } else {
        document.querySelector('#compose-subject').value = `Re: ${email.subject}`;
        document.querySelector('#compose-body').value = `On ${email.timestamp} ${email.sender} wrote: ${email.body}`;
      }
      
    });
    
  }

  //get form data
  document.querySelector("#compose-form").onsubmit = () => {
    const recipients = document.querySelector("#compose-recipients").value;
    const subject = document.querySelector("#compose-subject").value;
    const body = document.querySelector("#compose-body").value;

    //email
    fetch('/emails', {
      method: 'POST',
      body: JSON.stringify({
        recipients: recipients,
        subject: subject,
        body: body
      })
    });
    
    //load inbox
    load_mailbox("sent");

    return false;
  }

}

function load_mailbox(mailbox) {
  
  // Show the mailbox and hide other views
  document.querySelector("#email-view").style.display = 'none';
  document.querySelector('#emails-view').style.display = 'block';
  document.querySelector('#compose-view').style.display = 'none';

  // Show the mailbox name
  document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;

  
  fetch(`/emails/${mailbox}`)
  .then(response => response.json())
  .then(emails => {

    //for each email
    for (i=0; i<emails.length; i++) {
      create_email(emails[i]);
    }
      
  });
  
}

function create_email(email) {
  const send = document.createElement("span");
  send.className = 'sender';
  send.innerHTML = `${email.sender}`;

  const subject = document.createElement("span");
  subject.className ='subject';
  subject.innerHTML = `${email.subject}`;

  const time = document.createElement("span");
  time.className = 'time';
  time.innerHTML = `${email.timestamp}`;

  const div = document.createElement("div");
  div.className = 'email';
  div.append(send, subject, time);

  if (email.read === true) {
    div.style.backgroundColor = 'lightgray';
  };

  div.addEventListener("click", () => {
    load_email(email.id);
  });

  document.querySelector("#emails-view").append(div);
}

function load_email(id) {

  document.querySelector("#email-body").innerHTML = "";
  document.querySelector("#email-view").style.display = 'block';
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'none';

  fetch(`/emails/${id}`)
  .then(response => response.json())
  .then(email => {
    const body = email.body.split("\n");
    body.forEach(element => {
      let brk = document.createElement("br");
      document.querySelector("#email-body").append(element);
      document.querySelector("#email-body").append(brk);
    });
    document.querySelector("#to").innerHTML = email.recipients;
    document.querySelector("#from").innerHTML = email.sender;
    document.querySelector("#subject").innerHTML = email.subject;
    document.querySelector("#time").innerHTML = email.timestamp;

    if (email.archived === false) {
      const arch = document.querySelector("#archive");
      arch.innerHTML = "Archive";
      arch.onclick = () => {
        toggle_archive(id, false);
      }
    } else {
      const arch = document.querySelector("#archive");
      arch.innerHTML = "Unarchive"
      arch.onclick = () => {
        toggle_archive(id, true);
      }
    }

    document.querySelector("#reply").onclick = () => {
      compose_email(reply=true, id=id);
    };
  });

  fetch(`/emails/${id}`, {
    method: 'PUT',
    body: JSON.stringify({
        read: true
    })
  });

}

function toggle_archive(id, state) {
  fetch(`/emails/${id}`, {
    method: 'PUT',
    body: JSON.stringify({
      archived: !state
    })
  })
  .then(location.reload());
}