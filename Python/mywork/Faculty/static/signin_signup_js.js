

        function togglePassword(){
            const input = document.getElementById("signin_password");
            const icon = document.getElementById("toggle_icon");
            
            
            if(input.type === "password"){
                input.type = "text";
                icon.src = visibleIcon;
            }else{
                input.type = "password";

                icon.src = hiddenIcon;

            }
        }

        function toggleSignupPassword(){
            const input = document.getElementById("signup_password");
            const icon = document.getElementById("signup_toggle_icon");

            if(input.type === "password"){
                input.type = "text";
                icon.src = visibleIcon;

            }else{
                input.type = "password";
                icon.src = hiddenIcon;
            }
        }

        function toggle_Confirm_Password(){
            const confirm_password = document.getElementById("confirm_password");
            const confirm_toggle_icon = document.getElementById("confirm_toggle_icon");
             if(confirm_password.type === "password"){
                confirm_password.type = "text";
                confirm_toggle_icon.src = visibleIcon;
            }else{
                confirm_password.type = "password";
                confirm_toggle_icon.src = hiddenIcon;
            }
        }
    