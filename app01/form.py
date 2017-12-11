from django import forms
from django.forms import widgets as wd,ValidationError
from app01 import models

# class Question_form(forms.Form):
#     caption=forms.CharField(min_length=1,
#                             error_messages={'required':'不能为空'},
#                             widget=widgets.Textarea(attrs={"class":"form-control","style":"height: 40px"})
#                             )
#     type=forms.ChoiceField(choices=(
#                             (1,'打分（1~10）'),
#                             (2,'单选'),
#                             (3,'建议'),),
#                             widget=widgets.Select(attrs={"class":"form-control"}))


from django.forms import ModelForm

class QuestionModelForm(ModelForm):
    class Meta:
        model = models.Question
        fields = ['caption','tp']
        error_messages = {
            'caption': {'required': '不能为空', 'invalid': '格式错误'}
        }
        widgets = {
            'caption': wd.Input(attrs={'class': 'form-control caption_input',"style":"height: 40px"}),
            'tp': wd.Select(attrs={'class': 'form-control tp',"style":"width: 120px",})
        }


class OptionModelForm(ModelForm):
    class Meta:
        model = models.Option
        fields = ['name','score']
        widgets = {
            'name': wd.Input(attrs={'class': '',"style":"width: 80px"}),
            'score': wd.Input(attrs={'class': '',"style":"width: 80px"})
        }


class RegForm(forms.Form):
    user = forms.CharField(max_length=32,
                               min_length=5,
                               error_messages={'required': '用户名不能为空'},
                               widget=wd.TextInput(attrs={"class": "form-control", "placeholder": "请输入用户名"})
                               )
    pwd = forms.CharField(max_length=32,
                               min_length=6,
                               widget=wd.PasswordInput(
                                   attrs={"class": "form-control", "placeholder": "请输入密码"}
                               ))

    def clean_user(self):
        """
        钩子函数,判断用户名是否已存在
        :return:
        """
        ret = models.Student.objects.filter(user=self.cleaned_data.get("user"))
        if not ret:
            return self.cleaned_data.get("user")
        else:
            raise ValidationError("用户名已注册")

    def clean_pwd(self):
        """
        钩子函数，规定密码不能是全数字或全字母
        :return:
        """
        ret = self.cleaned_data.get("pwd")
        if ret.isdigit():
            raise ValidationError("密码不能全是数字")
        elif ret.isalpha():
            raise ValidationError("密码不能全是字母")
        else:
            return ret




