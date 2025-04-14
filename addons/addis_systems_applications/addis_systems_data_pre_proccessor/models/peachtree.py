from odoo import api, fields, models, exceptions,_
from odoo.http import request
from odoo import http
import os
import time
from odoo.exceptions import UserError

class PeachTreeFile(models.Model):
    _name = "peachtree.peachtreefile"
    _description = "record peachtree"
    _rec_name = 'title'
    title=fields.Char(string="Tittle",required=True)
    customerfile = fields.Binary(string='Customer File',required=True)
    vendorfile = fields.Binary(string='Vendor File')
    jrnl_rowfile = fields.Binary(string='Jrnl Row CSV File',required=True)
    jrnl_hdrfile = fields.Binary(string='Jrnl Hdr CSV File',required=True)
    chart_psvfile= fields.Binary(string='Chart PSV CSV File',required=True)
    chart_peachree=fields.Binary(string='Chart peachtree CSV File',required=True)
    tax_code= fields.Binary(string='Tax Code CSV File')
    tax_authority=fields.Binary(string='Tax Authority CSV File')
    @api.model
    def get_chart_data(self,data=[]):
        return {"jhr":98,"klm":312}






    def chart_replace(self,chart_dat):
        chart_dat=chart_dat.rename(columns={"Account ID":"AccountID"})
        chart_dat['Type'] = chart_dat['Type'].replace('Accounts Receivable', 'Receivable')
        chart_dat['Type'] = chart_dat['Type'].replace('Inventory', 'Current Assets')
        chart_dat['Type'] = chart_dat['Type'].replace('Other Current Assets', 'Current Assets')
        chart_dat['Type'] = chart_dat['Type'].replace('Fixed Assets', 'Fixed Assets')
        chart_dat['Type'] = chart_dat['Type'].replace('Accumulated Depreciation', 'Depreciation')
        chart_dat['Type'] = chart_dat['Type'].replace('Other Current Assets', 'Non-current Assets')
        chart_dat['Type'] = chart_dat['Type'].replace('Accounts Payable', 'Payable')
        chart_dat['Type'] = chart_dat['Type'].replace('Expenses', 'Expenses')
        chart_dat['Type'] = chart_dat['Type'].replace('Other Current Liabilities', 'Non-current Liabilities')
        chart_dat['Type'] = chart_dat['Type'].replace('Equity-gets closed', 'Equity')
        chart_dat['Type'] = chart_dat['Type'].replace('Equity-Retained Earnings', 'Current Year Earnings')
        chart_dat['Type'] = chart_dat['Type'].replace('Income', 'Income')
        chart_dat['Type'] = chart_dat['Type'].replace('Cost of Sales', 'Cost of Revenue')
        chart_dat['Type'] = chart_dat['Type'].replace('Cash', 'Bank and Cash')
        chart_dat['Type'] = chart_dat['Type'].replace('Other Assets', 'Current Assets')
        chart_dat['Type'] = chart_dat['Type'].replace('Long Term Liabilities', 'Non-current Liabilities')
        chart_dat['Type'] = chart_dat['Type'].replace('Equity-does not close', 'Equity')
        return chart_dat
    
    def direct_journal(self,jrnl_header,jrnlrow):
        postorders=jrnl_header[jrnl_header['GLAcntNumber']==0]["PostOrder"].values.tolist()
        new_jrnl_row = pd.DataFrame(
		columns=["AccountID","Amount","RowNumber","Reference","RowDate"]
        )
        for postorder in postorders:
            reference = jrnl_header[jrnl_header["PostOrder"]==postorder][["Reference"]].values.tolist()[0]
            jrnlrow_data=jrnlrow[jrnlrow["PostOrder"]==postorder][["Amount","RowNumber","AccountID","RowDate"]]
            filtered_df = jrnlrow_data[(jrnlrow_data['Amount']!=0) ]
            #filtered_df=filtered_df.drop_duplicates(subset="RowNumber", inplace=True)
            if not filtered_df.empty:
                filtered_df["Reference"]=reference+[""]*(len(filtered_df)-1)
                rowdate=filtered_df["RowDate"].values.tolist()[0]
                filtered_df["RowDate"]=[rowdate]+[""]*(len(filtered_df)-1)
                new_jrnl_row=pd.concat([new_jrnl_row,filtered_df],ignore_index=True)
        return new_jrnl_row





    def receipts(self,jrnl_header,jrnlrow):
        postorders=jrnl_header[jrnl_header['PaymentMethod'].notna()]["PostOrder"].values.tolist()
        new_jrnl_row = pd.DataFrame(
		columns=["CustomerID","AccountID","RowDescription","Amount","RowNumber","Reference","RowDate"])
        jrnl_data=pd.DataFrame(
                columns=["jrnl_name","jrnl_code","Type","Account"]
        )
        for postorder in postorders:
            reference = ["Customer Invoices"]
            jrnlrow_data=jrnlrow[jrnlrow["PostOrder"]==postorder][["Amount","RowNumber","AccountID","RowDescription","RowDate","CustomerID"]]
            filtered_df = jrnlrow_data[(jrnlrow_data['Amount']!=0)&(jrnlrow_data['RowNumber']!=0)]
            if not filtered_df.empty:
                filtered_df["Reference"]=reference+[""]*(len(filtered_df)-1)
                filtered_df["Tax"] =["VAT 0% rated sales"]*len(filtered_df)
                rowdate=filtered_df["RowDate"].values.tolist()[0]
                filtered_df["RowDate"]=[rowdate]+[""]*(len(filtered_df)-1)
                cust=filtered_df["CustomerID"].values.tolist()[0]
                filtered_df["CustomerID"]=[cust]+[""]*(len(filtered_df)-1)
                new_jrnl_row=pd.concat([new_jrnl_row,filtered_df],ignore_index=True)
        return new_jrnl_row
        

    def journal_entry(self,jrnl_header,jrnlrow):
        postorders=jrnl_header["PostOrder"].values.tolist()
        new_jrnl_row = pd.DataFrame(
		columns=["AccountID","Amount","RowNumber","Reference","RowDate"])
        for postorder in postorders:
            reference = jrnl_header[jrnl_header["PostOrder"]==postorder][["Reference"]].values.tolist()[0]
            jrnlrow_data=jrnlrow[jrnlrow["PostOrder"]==postorder][["Amount","RowNumber","AccountID","RowDate"]]
            filtered_df = jrnlrow_data[(jrnlrow_data['Amount']!=0) ]
            #filtered_df=filtered_df.drop_duplicates(subset="RowNumber", inplace=True)
            if not filtered_df.empty:
                filtered_df["Reference"]=reference+[""]*(len(filtered_df)-1)
                rowdate=filtered_df["RowDate"].values.tolist()[0]
                filtered_df["RowDate"]=[rowdate]+[""]*(len(filtered_df)-1)
                new_jrnl_row=pd.concat([new_jrnl_row,filtered_df],ignore_index=True)
        try:
            new_jrnl_row["AccountID"]=new_jrnl_row["AccountID"].apply(lambda x:float(x))
        except:
            pass

        return new_jrnl_row

    
    def process_journal_data(self):
        path = os.path.dirname(os.path.realpath(__file__))
        path=path.split("\\")
        k=path.index("odoo")
        path="/".join(path[:k])
        dest_path='odoo/addons/web/static/csv'
        path=os.path.join(path,dest_path)
        file_name_csv="journal_entry.csv"
        file_path=os.path.join(path, file_name_csv)

        ################ Reading CSV Files ##################################
        try:
            charts = pd.read_csv(io.BytesIO(base64.b64decode(self.chart_psvfile)))
            direct_chart=pd.read_csv(io.BytesIO(base64.b64decode(self.chart_peachree)))
            jrnl_header = pd.read_csv(io.BytesIO(base64.b64decode(self.jrnl_hdrfile)))
            jrnlrow=pd.read_csv(io.BytesIO(base64.b64decode(self.jrnl_rowfile)))
            customers=pd.read_csv(io.BytesIO(base64.b64decode(self.customerfile)))
        except:
            raise exceptions.ValidationError("Error Reading Files Make sure Your Files are CSV and It is not Opened in another App ")
        
        ############# Chart Of Accounts  ######################

        try:
            charts=charts[["AccountID","AccountDescription","GLAcntNumber"]]
            direct_chart=direct_chart.rename(columns={"Account ID":"AccountID"})
            charts=charts.merge(direct_chart[["Type","AccountID"]],on="AccountID",how="left")
            chart_dat=pd.read_csv(io.BytesIO(base64.b64decode(self.chart_peachree)))
            final_chart_of_accounts_data=self.chart_replace(chart_dat)
            filename = self.title+'chart_of_Accounts.csv'
            final_chart_of_accounts_data.to_csv(path+"/"+filename,index=False)
        except:
            raise exceptions.ValidationError("Error Reading Files Make sure Your Files are CSV")
        ############## General Journal Entry ################################################################
        try:
            jrnl_header=jrnl_header.merge(charts[["AccountID","GLAcntNumber"]],on="GLAcntNumber",how="left")
            jrnlrow=jrnlrow.merge(charts[["AccountID","GLAcntNumber"]],on="GLAcntNumber",how="left")
            journal_entries=self.journal_entry(jrnl_header,jrnlrow)
            filename = self.title+'all_journal_entries.csv'
            journal_entries.to_csv(path+"/"+filename,index=False)
        except:
            raise exceptions.ValidationError("Error Generating General Journal Entry Files Make sure Forms are filled Correctly")
        ############ Receipts ############################################################################
        try:
            jrnlrow=jrnlrow.merge(customers[["CustomerID","CustomerRecordNumber"]],on="CustomerRecordNumber",how="left")
            receipts_data=self.receipts(jrnl_header,jrnlrow)
            filename = self.title+'all_receipts.csv'
            receipts_data.to_csv(path+"/"+filename,index=False)
        except:
            raise exceptions.ValidationError("Error Generating Receipts Files Make sure Forms are filled Correctly")
        ###############################################3
        try:
            direct_jrnls=self.direct_journal(jrnl_header,jrnlrow)
            filename = self.title+'all_direct_jrnls.csv'
            direct_jrnls.to_csv(path+"/"+filename,index=False)
        except:
            raise exceptions.ValidationError("Error Generating Direct Journal Entries Files Make sure Forms are filled Correctly")
        return True

    def default(self):
        x=9
        return False

    def download_chart_of_accounts_data(self):
        self.process_journal_data()
        filename = self.title+'chart_of_Accounts.csv'
        return {
            'type': 'ir.actions.act_url',
            'name': filename,
            'url': '/web/static/csv/'+filename,
            'target': 'self',
            'res_model': 'peachtree.peachtreefile',
            'res_id': self.id,
            'context': http.request.env.context,
        }
    def download_all_journal_entries_data(self):
        self.process_journal_data()
        filename = self.title+'all_journal_entries.csv'
        return {
            'type': 'ir.actions.act_url',
            'name': filename,
            'url': '/web/static/csv/'+filename,
            'target': 'self',
            'res_model': 'peachtree.peachtreefile',
            'res_id': self.id,
            'context': http.request.env.context,
        }
    def download_all_receipts_data(self):
        self.process_journal_data()
        filename = self.title+'all_receipts.csv'
        return {
            'type': 'ir.actions.act_url',
            'name': filename,
            'url': '/web/static/csv/'+filename,
            'target': 'self',
            'res_model': 'peachtree.peachtreefile',
            'res_id': self.id,
            'context': http.request.env.context,
        }

    def download_all_direct_jrnls_data(self):
        self.process_journal_data()
        filename = self.title+'all_direct_jrnls.csv'
        return {
            'type': 'ir.actions.act_url',
            'name': filename,
            'url': '/web/static/csv/'+filename,
            'target': 'self',
            'res_model': 'peachtree.peachtreefile',
            'res_id': self.id,
            'context': http.request.env.context,
        }



