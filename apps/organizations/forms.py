from django import forms
from apps.operations.models import UserAsk

import re

# ModelForm,以从其它model里导入字段,从而快速生成form
class AddAskForm(forms.ModelForm):
    # 由于model并不具备min_length,所以mobile还得自己来写,它会覆盖掉model里对应的字段
    mobile=forms.CharField(max_length=11,min_length=11,required=True)
    
    class Meta:
        # model,指明来源于modeld的哪一张表
        model = UserAsk
        # fields,指明哪些字段需要生成,这里我们不需要生成add_time
        fields = ['name','mobile','course_name']

    # 对手机号进行正则匹配
    def clean_mobile(self):
        '''

        :return:
        '''
        mobile = self.cleaned_data['mobile']
        regex_mobile='^1[358]\d{9}$|^147\d{8}$|^176\d{8}$'
        p = re.compile(regex_mobile)
        if p.match(mobile):
            return mobile
        else:
            raise forms.ValidationError('手机号码非法',code='mobile_invalid')